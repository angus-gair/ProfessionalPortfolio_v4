/***************************************************************************************************************************************************

Author:       Angus Gair
Reviewers:    Bianca Xie & Yu Wang
Last updated: 2024-12-04
Version:      1.11v

OBJECTIVE:    Monthly KPIs for Everyday Rewards Program at BigW

NOTES:
    - Calculation Period: BigW Fiscal Month = BigWFiscalYearPeriod
        - Exceptions:
            - Boosters: last 8 weeks
            - Frequency: Monthly

    - `bigw_time_period_group_monthly` is a helper table, used to identify BIGW fiscal month periods and filter time periods. It is available via:
        - `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly`

    - `bigw_fact_member` is calculated weekly. The last week of the month is used to determine the status of the member for the month.
        - `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.vw_bigw_fact_member` is a view of:
            - `gcp-wow-rwds-ai-bi-prod.bigw.bigw_fact_member`

KEY ASSUMPTIONS MADE:

    - Non-Member Transactions are identified as: crn = '-1', '-2', '000'
    - Exclude Gift Card Sales: category = 'Gift Cards'
    - ATL Campaigns identified as: Campaign_Category = 'Points on product WSP'

DEFINITIONS:

    1. Members (Offer Status)
        - Booster   : Activate offer (via email, app) and shopped within last 8 weeks
        - Redeemer  : Redeem offer in selected period (BTL and ATL offers)

    2. Standard Sales Definition
        - Sales ($) = tot_amt_excld_gst_wo_wow  (what finance uses for sales, total sales no GST, no WOW dollar of base point)

        Exclusions:
            - Gift Cards

        Aggregation Level:
            - Basket Level

    3. AOV Sales Definition
        - Sales ($) = tot_amt_incld_gst (total paid by customers)

        Exclusions:
            - Gift Cards?????
            - Negative Sales (need to represent what customer purchased at point of sale)

        Aggregation Level:
            - Order Level (not Basket Level)

DEPENDENCIES:

    - Campaign Mapping Table: `gcp-wow-rwds-ai-pobe-dev.angus.bigw_marketingPlan_campaign_codes_static`

v1.03 =  Initial Version
v1.10 =  Significant changes to the code
        - Time Periods are all now by BigW Fiscal Month
        - Additional Metrics:
            - Added a Booster and Active Frequency
            - Added a Booster and Active Sales
            - Customer Annualised Sales
            - Acquisition from Group

***************************************************************************************************************************************************/

/*----------------------------------------------------------------------------------------------------------*/
/*                                              HELPER TABLES                                               */
/*----------------------------------------------------------------------------------------------------------*/
select * from `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` limit 10;
 

-- Time Period Group Table:

CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` AS

WITH base AS (
    SELECT DISTINCT
        FORMAT_DATE('%b-%E4Y', DATE(
            CASE WHEN dd.FiscalPeriodNumber <= 6 THEN dd.FiscalYear - 1 ELSE dd.FiscalYear END,
            CASE WHEN MOD((dd.FiscalPeriodNumber + 6), 12) = 0 THEN 12 ELSE CAST(MOD((dd.FiscalPeriodNumber + 6), 12) AS INT64) END,
            1
        )) AS fmonth,
        dd.FiscalYear * 100 + dd.FiscalPeriodNumber AS fmonth_order,
        FiscalPeriodStartDate,
        FiscalPeriodEndDate,
        FiscalYearStartDate,
        dd.FiscalPeriodNumber,
        dd.FiscalYear,
        DENSE_RANK() OVER (ORDER BY dd.FiscalYear * 100 + dd.FiscalPeriodNumber DESC) AS _rank
    FROM gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v dd
    WHERE FiscalPeriodEndDate < CURRENT_DATE("Australia/Sydney")  -- Potential leftover filter from testing
    ORDER BY _rank
)

, base2 AS (
    SELECT
        fmonth,
        CAST(fmonth_order AS STRING) AS fmonth_order,
        FiscalYear,
        'This Year' AS metric_type,
        FiscalPeriodStartDate,
        FiscalPeriodEndDate,
        FiscalYearStartDate,
        (DATE_DIFF(FiscalPeriodEndDate, FiscalPeriodStartDate, DAY) + 1) / 7 AS no_of_weeks,
        DENSE_RANK() OVER (ORDER BY FiscalPeriodStartDate DESC) AS month_number
    FROM base
    WHERE _rank <= 12

    UNION ALL

    SELECT
        b2.fmonth,
        CAST(b2.fmonth_order AS STRING) AS fmonth_order,
        b2.FiscalYear,
        'Last Year' AS metric_type,
        b2.FiscalPeriodStartDate,
        b2.FiscalPeriodEndDate,
        b2.FiscalYearStartDate,
        (DATE_DIFF(b2.FiscalPeriodEndDate, b2.FiscalPeriodStartDate, DAY) + 1) / 7 AS no_of_weeks,
        DENSE_RANK() OVER (ORDER BY b2.FiscalPeriodStartDate DESC) AS month_number
    FROM base b1
    INNER JOIN base b2 ON b1._rank = b2._rank - 12
    WHERE b1._rank <= 12

    UNION ALL

    SELECT
        b2.fmonth,
        CAST(b2.fmonth_order AS STRING) AS fmonth_order,
        b2.FiscalYear,
        '2 Years Ago' AS metric_type,
        b2.FiscalPeriodStartDate,
        b2.FiscalPeriodEndDate,
        b2.FiscalYearStartDate,
        (DATE_DIFF(b2.FiscalPeriodEndDate, b2.FiscalPeriodStartDate, DAY) + 1) / 7 AS no_of_weeks,
        DENSE_RANK() OVER (ORDER BY b2.FiscalPeriodStartDate DESC) AS month_number
    FROM base b1
    INNER JOIN base b2 ON b1._rank = b2._rank - 24
    WHERE b1._rank <= 12
    ORDER BY 8, 3
)

SELECT *,
    PARSE_DATE('%d-%b-%Y', CONCAT('01-', fmonth)) AS fmonth_date
FROM base2
ORDER BY 3
;

/* Output:

| fmonth | fmonth_order | FiscalYear | metric_type | FiscalPeriodStartDate | FiscalPeriodEndDate | FiscalYearStartDate | no_of_weeks | month_number | fmonth_date |
| ------ | ------------ | ---------- | ----------- | --------------------- | ------------------- | ------------------- | ----------- | ------------ | ----------- |
| Mar-22 | 202209       | 2022       | 2 Years Ago | 7/03/2022             | 3/04/2022           | 28/06/2021          | 4           | 9            | 1/03/2022   |
| Dec-21 | 202206       | 2022       | 2 Years Ago | 29/11/2021            | 2/01/2022           | 28/06/2021          | 5           | 12           | 1/12/2021   |
| May-22 | 202211       | 2022       | 2 Years Ago | 2/05/2022             | 29/05/2022          | 28/06/2021          | 4           | 7            | 1/05/2022   |
| Apr-22 | 202210       | 2022       | 2 Years Ago | 4/04/2022             | 1/05/2022           | 28/06/2021          | 4           | 8            | 1/04/2022   |
| Jun-22 | 202212       | 2022       | 2 Years Ago | 30/05/2022            | 26/06/2022          | 28/06/2021          | 4           | 6            | 1/06/2022   |
| Jan-22 | 202207       | 2022       | 2 Years Ago | 3/01/2022             | 30/01/2022          | 28/06/2021          | 4           | 11           | 1/01/2022   |
| Feb-22 | 202208       | 2022       | 2 Years Ago | 31/01/2022            | 6/03/2022           | 28/06/2021          | 5           | 10           | 1/02/2022   |
| Nov-22 | 202305       | 2023       | 2 Years Ago | 31/10/2022            | 27/11/2022          | 27/06/2022          | 4           | 1            | 1/11/2022   |
| Aug-22 | 202302       | 2023       | 2 Years Ago | 1/08/2022             | 4/09/2022           | 27/06/2022          | 5           | 4            | 1/08/2022   |
| Oct-22 | 202304       | 2023       | 2 Years Ago | 3/10/2022             | 30/10/2022          | 27/06/2022          | 4           | 2            | 1/10/2022   |

*/

/*----------------------------------------------------------------------------------------------------------*/
/*                                      MEMBER TYPE TEMP TABLE                                             */
/*----------------------------------------------------------------------------------------------------------*/

CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_member_type` AS (

WITH subs AS (
    SELECT DISTINCT
        crn,
        dd.BigWFiscalWeekEndDate AS fw_end_date,
        'EDR Subscriber' AS Member_Type
    FROM `gcp-wow-rwds-ai-subs-prod.EDX.EDX_daily_FCT_table` e
    INNER JOIN `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v` dd
        ON e.CalendarDay = dd.CalendarDay
    WHERE e.customer_type = 'Customer' AND e.event IN ('Paid')
)

, base AS (
    SELECT
        bf.FW_END_DATE,
        bf.CRN,
        bigw_booster_l4w_flag,
        IF(paid_everyday_extras_flag IS TRUE OR Member_Type = 'EDR Subscriber', TRUE, FALSE) AS paid_everyday_extras_flag,
        cust_type,
        IF(cust_type = 'Staff', TRUE, FALSE) AS staff_flag
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.edr_crn_flags_v` bf
    LEFT JOIN subs s
        ON s.fw_end_date = bf.FW_END_DATE
        AND s.crn = bf.CRN
    WHERE 1=1  -- Potential redundant filter
)

, base2 AS (
    SELECT *,
        CASE
            WHEN staff_flag IS TRUE THEN 'Staff'
            WHEN paid_everyday_extras_flag IS TRUE THEN 'EDR Subscriber'
            WHEN bigw_booster_l4w_flag IS TRUE THEN 'EDR Booster'
            ELSE 'EDR Member'
        END AS Member_Type
    FROM base
)

SELECT
    dd.CalendarDay,
    b2.FW_END_DATE,
    b2.CRN,
    b2.Member_Type
FROM base2 B2
INNER JOIN `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v` dd
    ON b2.FW_END_DATE = dd.CalendarDay
QUALIFY ROW_NUMBER() OVER (PARTITION BY dd.CalendarDay, b2.CRN ORDER BY b2.Member_Type DESC) = 1
);




/*----------------------------------------------------------------------------------------------------------*/
/*                                         BASKETS TEMP TABLE                                               */
/*----------------------------------------------------------------------------------------------------------*/

CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_baskets_ORDERID` AS (

WITH baskets AS (
    SELECT
        start_txn_date,
        CAST((dd.FiscalYear * 100 + dd.FiscalPeriodNumber) AS STRING) AS fmonth_order,
        COALESCE(bss.orderid, bas.basket_key) AS orderid,
        bas.crn,
        mt.Member_Type,
        SUM(tot_amt_incld_gst) AS sales_incl_gst
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.bi_article_sales_bigw` bas
    LEFT JOIN (
        SELECT DISTINCT
            bss.basketkey,
            bss.orderid
        FROM `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_integrated_sales_view.basket_sales_summary_v` bss
        WHERE POSNumber = 100
    ) bss
        ON bss.BasketKey = bas.basket_key
    INNER JOIN `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v` dd
        ON bas.start_txn_date = dd.CalendarDay
    LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_member_type` mt
        ON mt.CRN = bas.CRN
        AND mt.CalendarDay = bas.start_txn_date
    WHERE bas.crn NOT IN ('-1', '-2', '0', '000')
        AND bas.is_team_member IS NOT TRUE
        AND bas.tot_amt_incld_gst > 0
        AND bas.category <> 'Gift Cards'
        AND mt.Member_Type != 'Staff'
    GROUP BY 1, 2, 3, 4, 5
)

SELECT * FROM baskets

);





/*----------------------------------------------------------------------------------------------------------*/
/*                                         FREQUENCY DATA TABLE                                             */
/*----------------------------------------------------------------------------------------------------------*/

CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_freq_data` AS (

WITH padded_dates AS (
    SELECT
        tpg.fmonth_order,
        tpg.FiscalPeriodEndDate,
        tpg.FiscalPeriodStartDate,
        tpg.metric_type,
        dd.CalendarDay
    FROM `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg
    JOIN `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v` dd
        ON dd.CalendarDay BETWEEN tpg.FiscalPeriodStartDate AND tpg.FiscalPeriodEndDate
    -- Potential filter left from testing
    -- WHERE fmonth_order = '202505'
    ORDER BY dd.CalendarDay
)

SELECT DISTINCT
    pd.fmonth_order,
    b.orderid,
    b.crn,
    b.Member_Type,
    b.sales_incl_gst
FROM `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_baskets_ORDERID` b
JOIN padded_dates pd ON pd.CalendarDay = b.start_txn_date
WHERE pd.metric_type IN ('This Year', 'Last Year')

);




/*----------------------------------------------------------------------------------------------------------*/
/*                                         SCAN RATES TEMP TABLE                                            */
/*----------------------------------------------------------------------------------------------------------*/

CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_scan_rates` AS (

WITH scan_rates AS (
    SELECT
        tpg.fmonth,
        tpg.fmonth_order,
        SUM(CASE WHEN st.division = 'BIGW' THEN basket_count_scan END) / SUM(CASE WHEN st.division = 'BIGW' THEN basket_count END) AS scan_rate,
        SUM(CASE WHEN st.division = 'BIGW-Online' THEN basket_count_scan END) / SUM(CASE WHEN st.division = 'BIGW-Online' THEN basket_count END) AS online_scan_rate,
        SUM(CASE WHEN st.division = 'BIGW-InStore' THEN basket_count_scan END) / SUM(CASE WHEN st.division = 'BIGW-InStore' THEN basket_count END) AS instore_scan_rate,
        SUM(CASE WHEN st.division = 'BIGW' THEN total_sales END) AS total_sales,
        SUM(CASE WHEN st.division = 'BIGW' THEN total_sales_scan END) AS total_sales_scan
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.scan_tag_rates` st
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg ON st.fw_end_date BETWEEN tpg.FiscalPeriodStartDate AND tpg.FiscalPeriodEndDate
    GROUP BY 1, 2
)

, members AS (
    SELECT
        tpg.fmonth,
        tpg.fmonth_order,
        COUNT(DISTINCT bf.crn) AS active_members
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.vw_bigw_fact_member` bf
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg ON bf.fw_end_date = tpg.FiscalPeriodEndDate
    WHERE customer_segment IN ('Blue', 'New to BigW', 'Active', '1-T', 'Reactivated')
    GROUP BY 1, 2
)

, bas AS (
    SELECT
        start_txn_date,
        bas.crn,
        COUNT(DISTINCT basket_key) AS baskets,
        SUM(tot_amt_incld_gst) AS sales
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.bi_article_sales_bigw` bas
    WHERE crn NOT IN ('-1', '-2', '0', '000')
        AND category <> 'Gift Cards'
        AND tot_amt_incld_gst > 0
    GROUP BY 1, 2
)

, cas AS (  -- Customer Annualised Sales
    SELECT
        ref_mth,
        tpg.fmonth_order,
        COUNT(DISTINCT crn) AS members,
        SUM(bigw_total_cav) / COUNT(DISTINCT crn) AS AnnualMemberSpend
    FROM `gcp-wow-rwds-ai-sun-data-prod.group_cav.vw_active_group_cav_by_financial_month` a
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg
        ON a.ref_mth = tpg.fmonth_date
    GROUP BY 1, 2
    ORDER BY 1
)

SELECT
    fmonth_order,
    s.scan_rate,
    s.online_scan_rate,
    s.instore_scan_rate,
    m.active_members,
    s.total_sales,
    s.total_sales_scan,
    c.AnnualMemberSpend
FROM scan_rates s
JOIN members m USING (fmonth_order)
JOIN cas c USING (fmonth_order)
ORDER BY 1

);  -- End of table





/*----------------------------------------------------------------------------------------------------------*/
/*                                    EVERYDAY EXTRA TEMP TABLE                                             */
/*----------------------------------------------------------------------------------------------------------*/

CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_edX` AS (

-- Total Subscribers
WITH subscribers AS (
    SELECT
        tpg.FiscalPeriodEndDate,
        tpg.fmonth_order,
        COUNT(DISTINCT(SubscriberCustomerIdentifier)) AS subscribers
    FROM `gcp-wow-rwds-ai-subs-prod.EDX.EDX_daily_FCT_table` f
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg ON f.CalendarDay = tpg.FiscalPeriodEndDate
    LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_member_type` mt
        ON mt.CRN = f.CRN
        AND mt.CalendarDay = f.CalendarDay
    WHERE mt.Member_Type = 'EDR Subscriber'
    GROUP BY 1, 2
)

-- Monthly New Sign Ups
, monthly_new_subscribers AS (
    SELECT
        tpg.FiscalPeriodEndDate,
        tpg.fmonth_order,
        COUNT(DISTINCT(subscriber_customer_identifier)) AS new_subscribers
    FROM `gcp-wow-rwds-ai-subs-prod.EDX.EDX_subscriptions_data` e
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg ON e.overall_subs_start_date BETWEEN tpg.FiscalPeriodStartDate AND tpg.FiscalPeriodEndDate
    WHERE staff_plan_flag IS NULL
    GROUP BY 1, 2
)

-- Average Order Value
, AOV_subscriber AS (
    SELECT
        fmonth_order,
        SUM(sales_incl_gst) / COUNT(DISTINCT orderid) AS AOV_subscriber
    FROM `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_baskets_ORDERID`
    WHERE Member_Type = 'EDR Subscriber'
    GROUP BY 1
)

-- Frequency for Subscribers
, Freq_Month AS (
    SELECT
        fmonth_order,
        COUNT(DISTINCT orderid) / COUNT(DISTINCT crn) AS FREQ_monthly
    FROM `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_freq_data`
    WHERE Member_Type = 'EDR Subscriber'
    GROUP BY 1
)

SELECT
    tpg.fmonth,
    tpg.fmonth_order,
    s.subscribers,
    ns.new_subscribers,
    aov.AOV_subscriber,
    frq.FREQ_monthly AS edx_freq
FROM `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg
LEFT JOIN subscribers s USING (fmonth_order)
LEFT JOIN monthly_new_subscribers ns USING (fmonth_order)
LEFT JOIN AOV_subscriber aov USING (fmonth_order)
LEFT JOIN Freq_Month frq USING (fmonth_order)
ORDER BY 2

);  -- End of table





/*----------------------------------------------------------------------------------------------------------*/
/*                                     EVERYDAY REWARDS CALLOUT                                             */
/*----------------------------------------------------------------------------------------------------------*/

-- Helper Table: AMO Product Details with Campaign Start and End Dates

CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_AMO_PRODUCTS` AS (

-- Identify offer IDs for AMO campaigns
WITH AMO_offer_ids AS (
    SELECT DISTINCT
        offer_id,
        campaign_code,
        camp_type,
        Campaign_Category
    FROM `gcp-wow-rwds-ai-pobe-dev.angus.bigw_marketingPlan_campaign_codes_static`
    WHERE Campaign_Category = 'Points on product WSP'
)

-- Collect Campaign Details
, campaign_dets_AMO AS (
    SELECT DISTINCT
        ocm.campaign_code,
        oh.offer_nbr,
        oh.offer_name,
        CAST(oh.offer_start_date AS DATE) AS offer_start_date,
        CAST(oh.offer_end_date AS DATE) AS offer_end_date,
        OH.OfferLevelEE,
        audience_type_desc
    FROM `gcp-wow-rwds-ai-data-prod.rtl_data_model.offer_campaign_master` AS ocm
    INNER JOIN `gcp-wow-rwds-ai-data-prod.rtl_data_model.offer_header` AS oh ON ocm.offer_nbr = oh.offer_nbr
    INNER JOIN AMO_offer_ids aoi ON aoi.offer_id = ocm.offer_nbr AND ocm.campaign_code = aoi.campaign_code
    WHERE ocm.campaign_type = 'BIGW'
        AND oh.OfferLevelEE IN ('FIXED_POINTS_PRODUCTS', 'VARIABLE_POINTS_PRODUCTS')  -- Exclude basket points
    ORDER BY 1, 2
)

-- Collect Product Details
, AMO_PRODUCTS AS (
    SELECT DISTINCT
        art.ArticleWithUOM,
        art.SalesOrg,
        art.ArticleDescription,
        art.Article,
        art.BrandDescription,
        art.Brand,
        art.CategoryDescription,
        art.Sub_CategoryDescription,
        p.OfferLevelEE,
        p.offer_start_date,
        p.offer_end_date,
        p.offer_nbr,
        p.audience_type_desc
    FROM `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_article_master_v` AS art
    INNER JOIN (
        SELECT DISTINCT
            srd.prod_nbr,
            cda.OfferLevelEE,
            cda.offer_start_date,
            cda.offer_end_date,
            cda.offer_nbr,
            cda.audience_type_desc
        FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.vw_bi_sales_reward_details` srd
        INNER JOIN campaign_dets_AMO cda
            ON cda.offer_nbr = srd.offer_nbr
            AND cda.offer_start_date = CAST(srd.offer_start_date AS DATE)
    ) p
        ON CAST(p.prod_nbr AS STRING) = art.ArticleWithUOM
        AND SalesOrg = 1060
        AND NOT REGEXP_CONTAINS(CategoryDescription, '(?i)FEE|GIFT CARD|Home Delivery')
)

-- List of AMO products with campaign start and end dates
SELECT *
FROM AMO_PRODUCTS
QUALIFY ROW_NUMBER() OVER (PARTITION BY ArticleWithUOM, offer_start_date ORDER BY offer_start_date) = 1

);  -- End of table




/*----------------------------------------------------------------------------------------------------------*/
/*                                EVERYDAY REWARDS METRICS TEMP TABLE                                       */
/*----------------------------------------------------------------------------------------------------------*/

CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_EDR_Callouts` AS (

-- Monthly Redeemers and Sales by Redeemers

-- Identify BTL campaigns
WITH campaign_dets AS (
    SELECT DISTINCT
        mcc.fw_start_date,
        mcc.offer_id,
        mcc.campaign_code,
        mcc.camp_type,
        mcc.Campaign_Desc,
        mcc.Loyalty_funded
    FROM `gcp-wow-rwds-ai-pobe-dev.angus.bigw_marketingPlan_campaign_codes_static` mcc
    WHERE mcc.camp_type IN ('BTL')
        AND Loyalty_funded IS FALSE  -- Exclude campaigns paid for by Everyday Rewards
)

-- Identify BTL redemption baskets
, srd_basket AS (
    SELECT
        srd.fw_start_date,
        srd.fw_end_date,
        dd.BigWFiscalYearPeriod,
        dd.FiscalYear,
        srd.CRN,
        basket_key,
        srd.campaign_code,
        srd.offer_nbr,
        SUM(srd.sales_amt_incld_gst) AS sales
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.vw_bi_sales_reward_details` srd
    INNER JOIN `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v` dd
        ON srd.start_txn_date = dd.CalendarDay
    INNER JOIN campaign_dets cd
        ON srd.fw_start_date = cd.fw_start_date
            AND srd.offer_nbr = cd.offer_id
    WHERE srd.crn NOT IN ('-1', '-2', '0', '000')
        AND srd.category <> 'Gift Cards'
        AND srd.sales_amt_incld_gst > 0
        AND srd.division_nbr = '1060'
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
)

-- BTL Basket Sales: Redemption baskets and Sales
, bas AS (
    SELECT
        dd.FiscalYear,
        dd.BigWFiscalYearPeriod,
        CAST((dd.FiscalYear * 100 + dd.FiscalPeriodNumber) AS STRING) AS fmonth_order,
        bas.fw_end_date,
        bas.CRN,
        srb.crn AS crn_in_srb,
        bas.basket_key,
        srb.basket_key AS redemption_basket_key,
        srb.campaign_code,
        srb.offer_nbr,
        mt.Member_Type,
        MAX(CASE WHEN srb.crn IS NOT NULL THEN 1 ELSE 0 END) OVER (PARTITION BY bas.CRN, dd.FiscalYear, dd.BigWFiscalYearPeriod) AS Redeemer_flag,  -- Identify if redeemed during the month
        SUM(bas.tot_amt_excld_gst_wo_wow) AS sales
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.bi_article_sales_bigw` bas
    INNER JOIN `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v` dd
        ON bas.start_txn_date = dd.CalendarDay
    LEFT JOIN srd_basket srb USING (CRN, basket_key)
    LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_member_type` mt
        ON mt.CRN = bas.CRN
        AND mt.CalendarDay = bas.start_txn_date
    WHERE bas.category <> 'Gift Cards'
        AND bas.tot_amt_excld_gst_wo_wow > 0
        AND mt.Member_Type != 'Staff'
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
)

-- Aggregate Bi Article Sales from Basket to Monthly Level
, bas_agg AS (
    SELECT
        FiscalYear,
        fmonth_order,
        COUNT(DISTINCT(IF(CRN NOT IN ('-1', '-2', '0', '000') AND Redeemer_flag = 1, crn_in_srb, NULL))) AS monthly_redeemers,
        COUNT(DISTINCT(IF(CRN NOT IN ('-1', '-2', '0', '000'), crn_in_srb, NULL))) AS monthly_active_members,  -- Used to validate the count of active members
        COUNT(DISTINCT(IF(CRN NOT IN ('-1', '-2', '0', '000'), redemption_basket_key, NULL))) AS Redemptions,
        SUM(IF(CRN NOT IN ('-1', '-2', '0', '000') AND Redeemer_flag = 1, sales, NULL)) AS redeemer_sales,
        SUM(sales) AS Sales,
        SUM(IF(Redeemer_flag = 1, sales, NULL)) * 1.0 / SUM(sales) * 1.0 AS redeemer_sales_perc
    FROM bas
    GROUP BY 1, 2
)

-- Monthly Boosters
, booster_crns AS (
    SELECT DISTINCT
        tpg.fmonth,
        tpg.fmonth_order,
        FW_END_DATE,
        bf.crn
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.edr_crn_flags_v` bf
    JOIN `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg ON bf.FW_END_DATE = tpg.FiscalPeriodEndDate
    WHERE bigw_booster_l4w_flag = TRUE
)

, booster AS (
    SELECT
        fmonth_order,
        COUNT(DISTINCT crn) AS booster
    FROM booster_crns
    GROUP BY 1
    ORDER BY 1
)

-- Sales by Boosters
, booster_sales AS (
    SELECT
        b.FiscalYear,
        b.fmonth_order,
        SUM(b.sales) AS booster_sales
    FROM bas b
    INNER JOIN booster_crns bc
        ON b.fmonth_order = bc.fmonth_order AND b.crn = bc.crn
    GROUP BY 1, 2
    ORDER BY 2
)

-- Average Order Value for EDR Members
, AOV_edr AS (
    SELECT
        fmonth_order,
        SUM(sales_incl_gst) / COUNT(DISTINCT orderid) AS AOV_edr,
        COUNT(DISTINCT orderid) AS ActiveMemberShops 
    FROM `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_baskets_ORDERID`
    WHERE Member_Type = 'EDR Member'
    GROUP BY 1
    ORDER BY 1
)

-- Frequency for Boosters
, Freq_Boost AS (
    SELECT
        a.fmonth_order,
        COUNT(DISTINCT orderid) / COUNT(DISTINCT a.crn) AS boost_FREQ
    FROM `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_freq_data` a
    JOIN booster_crns b ON a.fmonth_order = b.fmonth_order AND a.CRN = b.crn
    WHERE Member_Type = 'EDR Member'
    GROUP BY a.fmonth_order
)

-- Frequency for Everyday Rewards Members
, edr_FREQ AS (
    SELECT
        a.fmonth_order,
        COUNT(DISTINCT orderid) / COUNT(DISTINCT a.crn) AS edr_FREQ
    FROM `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_freq_data` a
    WHERE Member_Type = 'EDR Member'
    GROUP BY a.fmonth_order
)

-- BTL Value per Member
, BTL_members AS (
    SELECT
        dd.FiscalYear,
        BigWFiscalYearPeriod,
        CAST((dd.FiscalYear * 100 + dd.FiscalPeriodNumber) AS STRING) AS fmonth_order,
        COUNT(DISTINCT srd.crn) AS Members,
        COUNT(DISTINCT IF(cd.offer_id IS NULL, NULL, srd.crn)) AS Members_BTL,
        SUM(IF(cd.offer_id IS NULL, 0, cost_50)) AS cost_50  -- Reward value, calculated at 50 bps
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.vw_bi_sales_reward_details` srd
    JOIN `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v` dd
        ON srd.start_txn_date = dd.CalendarDay
    LEFT JOIN campaign_dets cd
        ON cd.fw_start_date = srd.fw_start_date
            AND cd.offer_id = srd.offer_nbr
    LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_member_type` mt
        ON  mt.CRN = srd.CRN
        AND mt.CalendarDay = srd.start_txn_date
    WHERE   srd.division_nbr = '1060'
        AND srd.CRN NOT IN ('-1', '-2', '0', '000')
        AND srd.category <> 'Gift Cards'
        AND mt.Member_Type != 'Staff'
    GROUP BY 1, 2, 3
)

, members AS (
    SELECT
        tpg.fmonth,
        tpg.fmonth_order,
        COUNT(DISTINCT bf.crn) AS active_members
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.vw_bigw_fact_member` bf
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg ON bf.fw_end_date = tpg.FiscalPeriodEndDate
    WHERE customer_segment IN ('Blue', 'New to BigW', 'Active', '1-T', 'Reactivated')
    GROUP BY 1, 2
)

, active_12w AS (
    SELECT 
        fw_end_date,
        COUNT(DISTINCT crn) as active_12w_members
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.edr_crn_flags_v`
    GROUP BY fw_end_date
)

-- AMO Redemptions
, AMO_redemptions AS (
    SELECT
        dd.FiscalYear,
        CAST((dd.FiscalYear * 100 + dd.FiscalPeriodNumber) AS STRING) AS fmonth_order,
        COUNT(DISTINCT basket_key) AS amo_redemptions,
        COUNT(DISTINCT CRN) AS amo_redeemers
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.bi_article_sales_bigw` bas
    JOIN `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v` dd ON bas.start_txn_date = dd.CalendarDay
    JOIN `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_AMO_PRODUCTS` amo ON bas.prod_nbr = amo.ArticleWithUOM
        AND bas.start_txn_date BETWEEN amo.offer_start_date AND amo.offer_end_date
    WHERE bas.division_nbr = 1060
        AND bas.CRN NOT IN ('-1', '-2', '0', '000')
        AND bas.category != 'Gift Cards'
        AND bas.prod_qty > 0
    GROUP BY 1, 2
)

SELECT
    tpg.fmonth,
    tpg.fmonth_order,
    b.booster,
    bs.booster_sales,
    aov.AOV_edr,
    aov.ActiveMemberShops,
    bf.boost_FREQ,
    -- btl.cost_50 / mem.active_12w_members AS BTL_value_per_member, --active member definition
    SAFE_DIVIDE( btl.cost_50 , a12.active_12w_members) AS BTL_value_per_member, -- per redeemer definition
    agg.monthly_redeemers,
    agg.redeemer_sales,
    agg.redeemer_sales_perc,
    agg.Redemptions,
    amo.amo_redemptions,
    mem.active_members,
    btl.Members AS Members_all_btl,
    btl.Members_BTL,
    ef.edr_FREQ
FROM `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg
LEFT JOIN bas_agg agg USING (fmonth_order)
LEFT JOIN booster b USING (fmonth_order)
LEFT JOIN booster_sales bs USING (fmonth_order)
LEFT JOIN AOV_edr aov USING (fmonth_order)
LEFT JOIN BTL_members btl USING (fmonth_order)
LEFT JOIN AMO_redemptions amo USING (fmonth_order)
LEFT JOIN members mem USING (fmonth_order)
LEFT JOIN Freq_Boost bf USING (fmonth_order)
LEFT JOIN edr_FREQ ef USING (fmonth_order)
LEFT JOIN active_12w a12 on tpg.FiscalPeriodEndDate = a12.fw_end_date

);  -- End of table



/*----------------------------------------------------------------------------------------------------------*/
/*                                AQUISITION FROM GROUP                                       */
/*----------------------------------------------------------------------------------------------------------*/


CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_add_metrics` AS (

with bas as   
(
  select start_txn_date
    , bas.crn
    -- , count(distinct basket_key) as baskets
    -- , sum(tot_amt_incld_gst) as sales
  from `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.bi_article_sales_bigw` bas  
  where crn <> '000' 
    and category <> 'Gift Cards'
    and tot_amt_incld_gst > 0
  group by 1,2 

  union all

  select start_txn_date
    , bas.crn
    -- , count(distinct basket_key) as baskets
    -- , sum(tot_amt_incld_gst) as sales
  from `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.bi_article_sales_bigw_hist` bas  
  where crn <> '000'  
    and category <> 'Gift Cards'
    and tot_amt_incld_gst > 0
  group by 1,2 
)


, earliest_trans as (
  select crn
    , min(start_txn_date) as earliest_txn_date
  from bas
  group by 1
)

-- Full date dimension
, dim_date AS (
    SELECT
        tpg.fmonth_order,
        tpg.FiscalPeriodEndDate,
        tpg.FiscalPeriodStartDate,
        dd.FiscalWeekEndDate AS fw_end_date,
        dd.CalendarDay -- daily 
    FROM `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg
    JOIN `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v` dd
        ON dd.CalendarDay BETWEEN tpg.FiscalPeriodStartDate AND tpg.FiscalPeriodEndDate
    ORDER BY dd.CalendarDay
)


, earliest_edr_date AS (
    SELECT 
        crn,
        MIN(fw_end_date) AS first_edr_fw_end_date
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.edr_crn_flags_v`
    GROUP BY crn
)

, aquisition_from_grp_STG as (
SELECT 
    bf.fw_end_date,
    dd.fmonth_order,
    bf.crn,
    bf.first_scan,
    et.earliest_txn_date,
    fe.first_edr_fw_end_date,
    CASE 
        WHEN bf.fw_end_date = et.earliest_txn_date AND fe.first_edr_fw_end_date < et.earliest_txn_date THEN bf.crn
        ELSE null
    END AS acquisition_from_group
FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.vw_bigw_fact_member` bf
LEFT JOIN earliest_trans et ON bf.crn = et.crn
LEFT JOIN earliest_edr_date fe ON bf.crn = fe.crn
JOIN dim_date dd on bf.fw_end_date = dd.CalendarDay
)

, aquisition_from_grp as (
SELECT 
    fmonth_order,
    COUNT(DISTINCT(acquisition_from_group)) as acquisition_from_group
FROM aquisition_from_grp_STG
GROUP BY 1
)


-- Collect Campaign Details
, campaign_details AS (
    SELECT DISTINCT
        ocm.campaign_code,
        CAST(oh.offer_start_date AS DATE) AS offer_start_date,
        CAST(oh.offer_end_date AS DATE) AS offer_end_date
    FROM `gcp-wow-rwds-ai-data-prod.rtl_data_model.offer_campaign_master` AS ocm
    INNER JOIN `gcp-wow-rwds-ai-data-prod.rtl_data_model.offer_header` AS oh 
        ON ocm.offer_nbr = oh.offer_nbr
    WHERE 1=1 
    AND ocm.campaign_type = 'BIGW'
    AND UPPER(LEFT(Campaign_code, 3)) IN ('WAH','WCT','WCV','WEN','WEV','WLC','WOL','WSP')
    ORDER BY 1, 2
)


-- ATTRIBUTED Incremental Sales
, attributable_sales_stg AS (
    SELECT DISTINCT
        vw.fw_start_date, 
        dd.fw_end_date,
        dd.fmonth_order,
        SUM(vw.ATTRIBUTED_INC_SALES) AS ATTRIBUTED_INC_SALES
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_car_analytics.cp_att_crn_all_view` vw
    JOIN campaign_details cd
        ON vw.campaign_code = cd.campaign_code
       AND cd.offer_start_date BETWEEN (vw.campaign_start_date - INTERVAL 3 DAY) AND (vw.campaign_start_date + INTERVAL 3 DAY)
    JOIN dim_date dd ON vw.fw_start_date = dd.calendarDay
    GROUP BY 1,2,3
)

, attributable_sales AS (
SELECT 
    d.fmonth_order,
    SUM(a.ATTRIBUTED_INC_SALES) AS TOTAL_ATTRIBUTED_INC_SALES
FROM attributable_sales_stg a
LEFT JOIN dim_date d 
    ON d.CalendarDay = a.fw_start_date
GROUP BY d.fmonth_order
)


-- Final Select
SELECT
    tpg.fmonth,
    tpg.fmonth_order,
    att.TOTAL_ATTRIBUTED_INC_SALES,
    afg.acquisition_from_group

FROM `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg
LEFT JOIN attributable_sales att USING (fmonth_order)
LEFT JOIN aquisition_from_grp afg USING (fmonth_order)
ORDER BY 2

);




/************************************************************************************************
    --------------------           FINAL / OUTPUT TABLE              ---------------------------
/*************************************************************************************************/

/*

| Metric_Group   | Metric                                        | Unit              | Variable_Name                  | Variable_Order |
| -------------- | --------------------------------------------- | ----------------- | ------------------------------ | -------------- |
| OKR            | Value per member                              | A$                | BTL_value_per_member           | 1              |
| OKR            | Acquisition from Group                        | # members         | acquisition_from_group         | 2              |
| OKR            | Annual Member Spend                           | A$                | AnnualMemberSpend              | 3              |
| OKR            | Big W scan rate (Overall)                     | % of transactions | scan_rate                      | 4              |
| OKR            | Active members (26 weeks)                     | # members (m)     | active_members                 | 5              |
| EDR Callouts   | Active members shops (LM)                     | # members (m)     | ActiveMemberShops              | 6              |
| EDR Callouts   | Active member shop frequency (LM)             | # transactions    | FREQ_monthly                   | 7              |
| EDR Callouts   | Active member transaction value excl GST (LM) | A$                | AOV_edr                        | 8              |
| EDR Callouts   | Booster Redeemers (LM)                        | # redeermers      | monthly_redeemers              | 9              |
| EDR Callouts   | Booster shop frequency (LM)                   | # transactions    | boost_FREQ                     | 10             |
| EDR Callouts   | Booster transaction value excl GST (LM)       | A$                | booster_sales                  | 11             |
| EDR Callouts   | AMO redemptions (LM)                          | # transactions    | amo_redemptions                | 12             |
| Everyday Extra | Total paying subscribers                      | # subscribers     | subscribers                    | 13             |
| Everyday Extra | Monthly new sign-ups                          | # sign-ups        | new_subscribers                | 14             |
| Everyday Extra | EE average transaction value excl GST (LM)    | A$                | AOV_subscriber                 | 15             |
| Everyday Extra | EE member shop frequency (LM)                 | # transactions    | edx_freq                       | 16             |
| Member Price   | Number of offers redeemed (LM)                | # members         | Number of offers redeemed (LM) | 17             |
| Member Price   | New & reactivated members (LM)                | # members         | New & reactivated members (LM) | 18             |


*/



/*************************************************************************************************/
-- TRENDS

CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-data-prod.outbound.bigw_monthly_performance_trends` AS (

SELECT
    tpg.fmonth,
    tpg.fmonth_order,
    tpg.FiscalYear,
    tpg.month_number,
    tpg.metric_type,
    CAST(scr.AnnualMemberSpend     AS FLOAT64) AS AnnualMemberSpend,
    CAST(scr.scan_rate             AS FLOAT64) AS scan_rate,
    CAST(scr.online_scan_rate      AS FLOAT64) AS online_scan_rate,
    CAST(scr.instore_scan_rate     AS FLOAT64) AS instore_scan_rate,
    CAST(scr.active_members        AS FLOAT64) AS active_members,
    CAST(edx.subscribers           AS FLOAT64) AS subscribers,
    CAST(edx.new_subscribers       AS FLOAT64) AS new_subscribers,
    CAST(edx.AOV_subscriber        AS FLOAT64) AS AOV_subscriber,
    CAST(edx.edx_freq              AS FLOAT64) AS edx_freq,
    CAST(edr.booster               AS FLOAT64) AS booster,
    CAST(edr.booster_sales         AS FLOAT64) AS booster_sales,
    CAST(edr.AOV_edr               AS FLOAT64) AS AOV_edr,
    CAST(edr.edr_FREQ               AS FLOAT64) AS edr_FREQ,
    CAST(edr.ActiveMemberShops     AS FLOAT64) AS ActiveMemberShops,
    CAST(edr.boost_FREQ            AS FLOAT64) AS boost_FREQ,
    CAST(edr.BTL_value_per_member  AS FLOAT64) AS BTL_value_per_member,
    CAST(edr.monthly_redeemers     AS FLOAT64) AS monthly_redeemers,
    CAST(edr.redeemer_sales        AS FLOAT64) AS redeemer_sales,
    CAST(edr.redeemer_sales_perc   AS FLOAT64) AS redeemer_sales_perc,
    CAST(edr.Redemptions           AS FLOAT64) AS edr_redemptions,
    CAST(edr.amo_redemptions       AS FLOAT64) AS amo_redemptions,
    -- New Variables from temp_bigw_add_metrics
    CAST(ama.acquisition_from_group     AS FLOAT64) AS acquisition_from_group,
    CAST(0 AS FLOAT64) AS Number_of_offers_redeemed_LM, -- placeholders  
    CAST(0 AS FLOAT64) AS New_and_reactivated_members_LM, -- placeholders

    ROW_NUMBER() OVER (ORDER BY CAST(tpg.fmonth_order AS INT64) DESC) AS lag_fmonth_order

FROM `gcp-wow-rwds-ai-pobe-dev.angus.bigw_time_period_group_monthly` tpg
LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_scan_rates`   scr USING (fmonth_order) -- scan rates
LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_edX`          edx USING (fmonth_order) -- everyday extra
LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_EDR_Callouts` edr USING (fmonth_order) -- EDR callouts
LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.angus.temp_bigw_add_metrics`  ama USING (fmonth_order) -- newly added metrics
ORDER BY 2
);


-- METRICS

CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-data-prod.outbound.bigw_monthly_performance_metrics` AS (

WITH curr_unpivot AS (
    SELECT
        fmonth_order,
        lag_fmonth_order,
        FiscalYear,
        month_number,
        metric_type,
        metric_name,
        metric_value
    FROM `gcp-wow-rwds-ai-data-prod.outbound.bigw_monthly_performance_trends`
    UNPIVOT (
        metric_value FOR metric_name IN (
        BTL_value_per_member,
        acquisition_from_group ,
        AnnualMemberSpend,
        scan_rate,
        active_members ,
        ActiveMemberShops,
        edr_FREQ,
        AOV_edr,
        monthly_redeemers ,
        boost_FREQ  ,
        booster_sales ,
        amo_redemptions,
        subscribers,
        new_subscribers,
        AOV_subscriber,
        edx_freq,
        Number_of_offers_redeemed_LM,
        New_and_reactivated_members_LM
        )
    )
    ORDER BY fmonth_order, metric_name
),

LM AS (
    SELECT * FROM curr_unpivot
    WHERE lag_fmonth_order = 2
),

SPLY AS (
    SELECT * FROM curr_unpivot
    WHERE metric_type = 'Last Year'
),

final_enhancement AS (
    SELECT
        cu.* EXCEPT(metric_value),
        cu.metric_value AS current_month,
        SAFE_DIVIDE((cu.metric_value - lm.metric_value), lm.metric_value) AS vs_LM,
        SAFE_DIVIDE((cu.metric_value - SPLY.metric_value), SPLY.metric_value) AS vs_SPLY,
        CASE
            WHEN cu.metric_name = 'BTL_value_per_member'                THEN 1
            WHEN cu.metric_name = 'acquisition_from_group'             THEN 2
            WHEN cu.metric_name = 'AnnualMemberSpend'                   THEN 3
            WHEN cu.metric_name = 'scan_rate'                           THEN 4
            WHEN cu.metric_name = 'active_members'                     THEN 5
            WHEN cu.metric_name = 'ActiveMemberShops'                   THEN 6
            WHEN cu.metric_name = 'edr_FREQ'                            THEN 7
            WHEN cu.metric_name = 'AOV_edr'                             THEN 8
            WHEN cu.metric_name = 'monthly_redeemers'                  THEN 9
            WHEN cu.metric_name = 'boost_FREQ'                        THEN 10
            WHEN cu.metric_name = 'booster_sales'                      THEN 11
            WHEN cu.metric_name = 'amo_redemptions'                     THEN 12
            WHEN cu.metric_name = 'subscribers'                         THEN 13
            WHEN cu.metric_name = 'new_subscribers'                     THEN 14
            WHEN cu.metric_name = 'AOV_subscriber'                      THEN 15
            WHEN cu.metric_name = 'edx_freq'                            THEN 16
            WHEN cu.metric_name = 'Number_of_offers_redeemed_LM'        THEN 17 -- placeholder
            WHEN cu.metric_name = 'New_and_reactivated_members_LM'        THEN 18 -- placeholder


            ELSE 99
        END AS metric_order,
        CASE
            WHEN cu.metric_name = 'BTL_value_per_member'                THEN 'Value per member'
            WHEN cu.metric_name = 'acquisition_from_group'             THEN 'Acquisition from Group'
            WHEN cu.metric_name = 'AnnualMemberSpend'                   THEN 'Annual Member Spend'
            WHEN cu.metric_name = 'scan_rate'                           THEN 'Big W scan rate (Overall)'
            WHEN cu.metric_name = 'active_members'                     THEN 'Active members (26 weeks)'
            WHEN cu.metric_name = 'ActiveMemberShops'                   THEN 'Active members shops (LM)'
            WHEN cu.metric_name = 'edr_FREQ'                            THEN 'Active member shop frequency (LM)'
            WHEN cu.metric_name = 'AOV_edr'                             THEN 'Active member transaction value excl GST (LM)'
            WHEN cu.metric_name = 'monthly_redeemers'                  THEN 'Booster Redeemers (LM)'
            WHEN cu.metric_name = 'boost_FREQ'                        THEN 'Booster shop frequency (LM)'
            WHEN cu.metric_name = 'booster_sales'                      THEN 'Booster transaction value excl GST (LM)'
            WHEN cu.metric_name = 'amo_redemptions'                     THEN 'AMO redemptions (LM)'
            WHEN cu.metric_name = 'subscribers'                         THEN 'Total paying subscribers'
            WHEN cu.metric_name = 'new_subscribers'                     THEN 'Monthly new sign-ups'
            WHEN cu.metric_name = 'AOV_subscriber'                      THEN 'EE average transaction value excl GST (LM)'
            WHEN cu.metric_name = 'edx_freq'                            THEN 'EE member shop frequency (LM)'
            WHEN cu.metric_name = 'Number_of_offers_redeemed_LM'        THEN 'Number of offers redeemed (LM)'
            WHEN cu.metric_name = 'New_and_reactivated_members_LM'        THEN 'New & reactivated members (LM)'

            ELSE '99'
        END AS Display_Name,
        -- old code needs to be updated
        CASE
            WHEN cu.metric_name IN ('scan_rate', 'instore_scan_rate', 'online_scan_rate') THEN '% of transactions'
            WHEN cu.metric_name IN ('active_members', 'edr_redemptions', 'booster', 'subscribers', 'new_subscribers', 'acquisition_from_group') THEN '# members'
            WHEN cu.metric_name IN ('amo_redemptions', 'boost_FREQ', 'edx_freq') THEN '# transactions'
            WHEN cu.metric_name IN ('redeemer_sales', 'AOV_edr', 'BTL_value_per_member', 'AOV_subscriber') THEN 'A$'
            ELSE 'OTHER'
        END AS metric_unit,
        SPLY.metric_value AS SPLY
    FROM curr_unpivot cu
    JOIN LM USING (metric_name)
    JOIN SPLY
        ON cu.metric_name = SPLY.metric_name
        AND cu.month_number = SPLY.month_number
    WHERE cu.lag_fmonth_order = 1
)

SELECT
    metric_order, 
    CASE
        WHEN metric_order BETWEEN 1 AND 5     THEN 'OKR'
        WHEN metric_order BETWEEN 6 AND 12    THEN 'EDR Callouts'
        WHEN metric_order BETWEEN 13 AND 16   THEN 'Everyday Extra'
        WHEN metric_order BETWEEN 17 AND 18   THEN 'Member Pricing'
        ELSE 'Other'
    END AS metric_category,
    Display_Name,
    current_month,
    vs_LM,
    vs_SPLY,
    SPLY,
    fmonth_order
FROM final_enhancement
ORDER BY metric_order

);
