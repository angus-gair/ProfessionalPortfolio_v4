/*
 * Points Cost Forecast Production SQL Script
 * ==========================================
 * 
 * Purpose: This script consolidates all SQL logic needed for the BigW Points Cost Forecast dashboard.
 *          It handles the extraction, transformation, and loading of data including:
 *          - Finance metrics and actuals
 *          - Sales forecasts
 *          - Campaign costs and forecasts
 *          - Everyday Extra costs
 *          - Comparison of actuals vs forecasts
 * 
 * Date: 2025-05-09
 * Version: 1.0
 * 
 * Dependencies:
 *  - BigW Finance System Data
 *  - Loyalty Analytics Data 
 *  - Campaign forecast JSON data
 *  - BigW destination business mappings
 *
 * Execution Plan:
 *  1. Create common dimension tables
 *  2. Extract finance actuals and forecasts
 *  3. Process campaign costs and forecasts
 *  4. Extract Everyday Extra data
 *  5. Combine all data into final dashboard tables
 */

-- =====================================================================================
-- STEP 1: CREATE COMMON DIMENSION TABLES
-- =====================================================================================

-- Create calendar dimension for FY24 and FY25
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_date` AS (
    SELECT 
        CalendarDay,
        FiscalWeekYear,
        FiscalWeek,
        FiscalWeekEndDate,
        FiscalYear,
        CONCAT(CAST(FiscalYear AS STRING), RIGHT(CONCAT('0000', CAST(BigWFiscalYearPeriod AS STRING)),3)) AS Fiscal_Period,
        FiscalWeekStartDate,
        BigWFiscalYear,
        BigWFiscalYearPeriod,
        BigWFiscalWeek,
        FORMAT_DATE('%a', CalendarDay) AS DayOfWeek,
        WeekDayNumber
    FROM `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v`
    WHERE FiscalYear IN (2024, 2025)
);

-- Create a business category mapping dimension
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_business_category` AS (
    SELECT DISTINCT 
        bd.Business, 
        bd.Category,
        bd.SubCategory
    FROM `gcp-wow-rwds-ai-data-prod.outbound.BigW_Destination_Business` bd
    UNION ALL
    SELECT 'General', 'General', 'General'
    UNION ALL
    SELECT NULL, NULL, NULL
);

-- Create a calendar day-of-week weights table for distributing weekly values to daily
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_day_of_week_weights` AS (
    SELECT 
        DayOfWeek,
        CASE 
            WHEN DayOfWeek = 'Mon' THEN 0.11177997
            WHEN DayOfWeek = 'Tue' THEN 0.127127373
            WHEN DayOfWeek = 'Wed' THEN 0.134606815
            WHEN DayOfWeek = 'Thu' THEN 0.163947143
            WHEN DayOfWeek = 'Fri' THEN 0.153884247
            WHEN DayOfWeek = 'Sat' THEN 0.178675994
            WHEN DayOfWeek = 'Sun' THEN 0.129978458
            ELSE 0 
        END AS daily_weight
    FROM (
        SELECT DISTINCT FORMAT_DATE('%a', CalendarDay) AS DayOfWeek
        FROM `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v`
    )
);

-- =====================================================================================
-- STEP 2: EXTRACT FINANCE ACTUALS AND FORECASTS
-- =====================================================================================

-- Finance actuals table - captures actual sales and financial metrics from BigW Finance System
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.finance_actuals` AS (
    SELECT 
        dd.FiscalYear,
        dd.FiscalWeekYear,
        dd.FiscalWeek,
        dd.FiscalWeekStartDate,
        dd.Fiscal_Period,
        fp.MerchandiseManager_Department AS Business_profit_v,
        fp.Category,
        SUBSTR(fp.Category, 3) AS CategoryWithoutCompanyCode,
        fp.Category_Description AS Category_Description_profit_v,
        CASE 
            WHEN fp.Sales_Channel LIKE 'HD%' THEN 'Online' 
            WHEN fp.Sales_Channel LIKE 'CC%' THEN 'Online' 
            ELSE 'Instore' 
        END AS SalesChannel_Cat,
        SUM(fp.Sales_InclTax) AS Sales_InclGST,
        SUM(fp.Sales_ExclTax) AS Net_Sales,
        SUM(fp.Scanback) AS Scanback,
        SUM(fp.Total_Discounts + fp.LoyaltyRewards) AS Total_Discounts_And_Rewards,
        SUM(fp.COGS) AS COGS,
        SUM(fp.Gross_Profit) AS Gross_Profit,
        CURRENT_TIMESTAMP() AS data_extraction_timestamp
    FROM `gcp-wow-ent-im-tbl-prod.gs_bigw_fin_data.fin_bigw_profit_v` fp
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_date` dd ON fp.Calendar_Day = dd.CalendarDay
    WHERE fp.SalesOrg IN ("1060")
      AND fp.Calendar_Day BETWEEN '2023-06-26' AND CURRENT_DATE()
      AND fp.MerchandiseManager_Code NOT IN ('MM922_AU', 'MM003_AU')
      AND fp.Category_Description != 'CIGARETTES'
      AND fp.Value_Type_Description = 'Actuals'
    GROUP BY 1,2,3,4,5,6,7,8,9,10
);

-- Finance forecast table - captures forecasted sales for future periods
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.finance_forecast` AS (
    SELECT 
        dd.FiscalYear,
        dd.FiscalWeekYear,
        dd.FiscalWeek,
        dd.FiscalWeekStartDate,
        dd.Fiscal_Period,
        fp.MerchandiseManager_Department AS Business_profit_v,
        fp.Category,
        SUBSTR(fp.Category, 3) AS CategoryWithoutCompanyCode,
        fp.Category_Description AS Category_Description_profit_v,
        SUM(COALESCE(fp.Sales_Merch_Forecast, 0)) AS Sales_Forecast,
        CURRENT_TIMESTAMP() AS data_extraction_timestamp
    FROM `gcp-wow-ent-im-tbl-prod.gs_bigw_fin_data.fin_bigw_profit_v` fp
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_date` dd ON fp.Calendar_Day = dd.CalendarDay
    WHERE fp.fiscal_year IN ('2024','2025')
      AND fp.Value_Type_Description = 'Merch Forecast'
      AND fp.SalesOrg IN ('1060')
      AND fp.MerchandiseManager_Code NOT IN ('MM922_AU', 'MM003_AU')
      AND fp.Category_Description != 'CIGARETTES'
    GROUP BY 1,2,3,4,5,6,7,8,9
);

-- Map finance data to business/category dimensions
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.finance_mapped` AS (
    -- Actuals with Business/Category mapping
    SELECT 
        fa.FiscalYear,
        fa.FiscalWeekYear,
        fa.FiscalWeek,
        fa.FiscalWeekStartDate,
        fa.Fiscal_Period,
        COALESCE(bc.Business, 'General Merch') AS Business,
        COALESCE(bc.Category, 'General Merch') AS Category,
        fa.CategoryWithoutCompanyCode,
        fa.Category_Description_profit_v,
        fa.SalesChannel_Cat,
        fa.Sales_InclGST,
        fa.Net_Sales,
        fa.Scanback,
        fa.Total_Discounts_And_Rewards,
        fa.COGS,
        fa.Gross_Profit,
        'Actual' AS DataType,
        fa.data_extraction_timestamp
    FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.finance_actuals` fa
    LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_business_category` bc
        ON UPPER(bc.SubCategory) = UPPER(fa.Category_Description_profit_v)
        
    UNION ALL
    
    -- Forecasts with Business/Category mapping
    SELECT 
        ff.FiscalYear,
        ff.FiscalWeekYear,
        ff.FiscalWeek,
        ff.FiscalWeekStartDate,
        ff.Fiscal_Period,
        COALESCE(bc.Business, 'General Merch') AS Business,
        COALESCE(bc.Category, 'General Merch') AS Category,
        ff.CategoryWithoutCompanyCode,
        ff.Category_Description_profit_v,
        NULL AS SalesChannel_Cat, -- Not available in forecasts
        NULL AS Sales_InclGST, -- Using forecast instead
        ff.Sales_Forecast AS Net_Sales,
        NULL AS Scanback, -- Not available in forecasts
        NULL AS Total_Discounts_And_Rewards, -- Not available in forecasts
        NULL AS COGS, -- Not available in forecasts
        NULL AS Gross_Profit, -- Not available in forecasts
        'Forecast' AS DataType,
        ff.data_extraction_timestamp
    FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.finance_forecast` ff
    LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_business_category` bc
        ON UPPER(bc.SubCategory) = UPPER(ff.Category_Description_profit_v)
);

-- Get actual sales data from article sales for more granular view
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.article_sales_actuals` AS (
    SELECT 
        bas.start_txn_date,
        dd.FiscalYear,
        dd.FiscalWeekYear,
        dd.FiscalWeek,
        dd.FiscalWeekStartDate, 
        COALESCE(bd.Business, 'General Merch') AS Business,
        COALESCE(bd.Category, 'General Merch') AS Category,
        CASE 
            WHEN bas.sales_channel_desc IN ('HD', 'CC') THEN 'Online' 
            ELSE 'Instore' 
        END AS SalesChannel_Cat,
        COALESCE(art.CategoryDescription, 'Unknown') AS CategoryDescription,
        SUM(bas.tot_amt_incld_gst) AS tot_amt_incld_gst,
        SUM(bas.tot_amt_excld_gst_wo_wow) AS tot_amt_excld_gst_wo_wow,
        SUM(bas.tot_amt_excld_gst_wt_wow) AS tot_amt_excld_gst_wt_wow,
        COUNT(DISTINCT bas.basket_key) AS basket_count,
        COUNT(DISTINCT bas.crn) AS customer_count,
        CURRENT_TIMESTAMP() AS data_extraction_timestamp
    FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.bi_article_sales_bigw` bas  
    LEFT JOIN `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_article_master_v` art
        ON bas.prod_nbr = art.ArticleWITHUOM AND bas.division_nbr = art.SalesOrg
    LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_business_category` bd
        ON bd.SubCategory = INITCAP(art.CategoryDescription)
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_date` dd 
        ON bas.start_txn_date = dd.CalendarDay
    WHERE bas.category <> 'Gift Cards'
      AND bas.tot_amt_incld_gst > 0
      AND bas.division_nbr = 1060
      AND dd.FiscalYear IN (2024, 2025)
    GROUP BY 1,2,3,4,5,6,7,8,9
);

-- Create helper table for complete time x business x category combinations
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.helper_dimension_combinations` AS (
    SELECT 
        dd.FiscalYear,
        dd.FiscalWeekYear,
        dd.FiscalWeek,
        dd.FiscalWeekStartDate,
        dd.FiscalWeekEndDate,
        dd.CalendarDay,
        bc.Business,
        bc.Category
    FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_date` dd
    CROSS JOIN (
        SELECT DISTINCT Business, Category 
        FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_business_category`
        WHERE Business IS NOT NULL AND Category IS NOT NULL
    ) bc
    WHERE dd.FiscalYear IN (2024, 2025)
);

-- =====================================================================================
-- STEP 3: PROCESS CAMPAIGN COSTS AND FORECASTS
-- =====================================================================================

-- Process campaign details and structure campaign streams
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.campaign_details` AS (
    SELECT
        REGEXP_REPLACE(campaignStream, r'[\r\n\t]', '') AS campaignStream,
        CampaignDetails,
        fw_CampaignStartDate,
        fw_CampaignStartDate AS FiscalWeekStartDate, -- For joining
        year,
        Campaign_Start_Date,
        Campaign_End_Date,
        SPLIT(CampaignStream, '_')[OFFSET(1)] AS CampaignType,
        CASE 
            WHEN ARRAY_LENGTH(SPLIT(CampaignStream, '_')) > 2 THEN SPLIT(CampaignStream, '_')[OFFSET(2)]
            ELSE NULL
        END AS CampaignSubType,
        Include_Categories,
        CASE 
            WHEN REGEXP_CONTAINS(campaignStream, r'_XBan_') THEN 'XBan'
            WHEN REGEXP_CONTAINS(campaignStream, r'_ATL_') THEN 'ATL'
            WHEN REGEXP_CONTAINS(campaignStream, r'_BTL_') THEN 'BTL'
            WHEN REGEXP_CONTAINS(campaignStream, r'_Trade_') THEN 'Trade'
            WHEN REGEXP_CONTAINS(campaignStream, r'_Category_') THEN 'Category'
            WHEN REGEXP_CONTAINS(campaignStream, r'_EDX_') THEN 'Everyday Extra'
            ELSE NULL 
        END AS CampaignCategoryType,
        DATE_DIFF(Campaign_End_Date, Campaign_Start_Date, DAY) + 1 AS campaign_duration,
        costs_budget_fcast,
        ROW_NUMBER() OVER () AS campaign_row_id
    FROM `gcp-wow-rwds-ai-pobe-dev.angus.bigw_campaign_details_planOnPage_FY25_PART2_static`
);

-- Process campaign costs forecast from the marketing plan
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.campaign_costs_forecast` AS (
    WITH forecast_base AS (
        -- Extract campaign cost foreacasts by week and category
        SELECT 
            cd.campaignStream,
            cd.CampaignCategoryType,
            cd.FiscalWeekStartDate,
            bc.Business,
            bc.Category,
            dd.FiscalWeekYear,
            dd.FiscalYear,
            dd.FiscalWeek,
            cd.costs_budget_fcast,
            -- Apply standard costs based on forecast % of budget
            cd.costs_budget_fcast * 0.0050 AS cost_50bps_forecast,
            cd.costs_budget_fcast * 0.0020 AS cost_20bps_forecast,
            cd.costs_budget_fcast * 0.0070 AS cost_70bps_forecast
        FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.campaign_details` cd
        CROSS JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_business_category` bc
        INNER JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_date` dd 
            ON cd.FiscalWeekStartDate = dd.FiscalWeekStartDate
        WHERE cd.costs_budget_fcast > 0
    ),
    
    -- Calculate proportional allocation of campaign costs to business/category
    -- We'll use sales forecast as the driver for allocation
    sales_proportions AS (
        SELECT 
            fb.FiscalWeekYear,
            fb.Business,
            fb.Category,
            fb.Net_Sales,
            SUM(fb.Net_Sales) OVER (PARTITION BY fb.FiscalWeekYear) AS total_sales_week,
            SAFE_DIVIDE(fb.Net_Sales, SUM(fb.Net_Sales) OVER (PARTITION BY fb.FiscalWeekYear)) AS sales_proportion
        FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.finance_mapped` fb
        WHERE fb.DataType = 'Forecast'
        QUALIFY ROW_NUMBER() OVER (PARTITION BY fb.FiscalWeekYear, fb.Business, fb.Category ORDER BY fb.data_extraction_timestamp DESC) = 1
    )
    
    SELECT
        f.campaignStream,
        f.CampaignCategoryType,
        f.FiscalWeekStartDate,
        f.FiscalWeekYear,
        f.FiscalYear,
        f.FiscalWeek,
        CASE
            -- For storewide campaigns, distribute based on sales proportions 
            WHEN f.Include_Categories = 'Storewide' THEN sp.Business
            -- For category specific campaigns, use the mapped business
            ELSE f.Business
        END AS Business,
        CASE
            -- For storewide campaigns, distribute based on sales proportions
            WHEN f.Include_Categories = 'Storewide' THEN sp.Category
            -- For category specific campaigns, use the mapped category
            ELSE f.Category
        END AS Category,
        -- Apply proportional allocation for costs
        CASE
            WHEN f.Include_Categories = 'Storewide' THEN f.cost_50bps_forecast * COALESCE(sp.sales_proportion, 0)
            ELSE f.cost_50bps_forecast
        END AS cost_50bps_forecast,
        CASE
            WHEN f.Include_Categories = 'Storewide' THEN f.cost_20bps_forecast * COALESCE(sp.sales_proportion, 0)
            ELSE f.cost_20bps_forecast
        END AS cost_20bps_forecast,
        CASE
            WHEN f.Include_Categories = 'Storewide' THEN f.cost_70bps_forecast * COALESCE(sp.sales_proportion, 0)
            ELSE f.cost_70bps_forecast
        END AS cost_70bps_forecast,
        CURRENT_TIMESTAMP() AS data_extraction_timestamp
    FROM forecast_base f
    LEFT JOIN sales_proportions sp
        ON f.FiscalWeekYear = sp.FiscalWeekYear
        -- Only join for storewide campaigns that need to be distributed
        AND f.Include_Categories = 'Storewide'
);

-- Create daily forecast of campaign costs
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.campaign_costs_forecast_daily` AS (
    SELECT
        dd.CalendarDay,
        cf.campaignStream,
        cf.CampaignCategoryType,
        cf.Business,
        cf.Category,
        cf.FiscalWeekYear,
        cf.FiscalYear,
        cf.FiscalWeek,
        dw.DayOfWeek,
        dw.daily_weight,
        -- Apply daily distribution weights
        cf.cost_50bps_forecast * dw.daily_weight AS cost_50bps_forecast_daily,
        cf.cost_20bps_forecast * dw.daily_weight AS cost_20bps_forecast_daily,
        cf.cost_70bps_forecast * dw.daily_weight AS cost_70bps_forecast_daily,
        cf.data_extraction_timestamp
    FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.campaign_costs_forecast` cf
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_date` dd
        ON cf.FiscalWeekStartDate = dd.FiscalWeekStartDate
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_day_of_week_weights` dw
        ON dw.DayOfWeek = dd.DayOfWeek
    WHERE dd.FiscalWeekStartDate BETWEEN cf.FiscalWeekStartDate AND DATE_ADD(cf.FiscalWeekStartDate, INTERVAL 6 DAY)
);

-- Campaign actuals - extract campaign cost actuals from finance system
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.campaign_costs_actuals` AS (
    SELECT
        dd.CalendarDay,
        dd.FiscalWeekYear,
        dd.FiscalYear,
        dd.FiscalWeek,
        dd.FiscalWeekStartDate,
        COALESCE(bd.Business, 'General Merch') AS Business,
        COALESCE(bd.Category, 'General Merch') AS Category,
        fp.Controller_Description AS campaign_controller,
        fp.Offer_ID_DC AS offer_id,
        fp.Category_Description AS category_description,
        CASE 
            WHEN fp.Sales_Channel LIKE 'HD%' THEN 'Online' 
            WHEN fp.Sales_Channel LIKE 'CC%' THEN 'Online' 
            ELSE 'Instore' 
        END AS SalesChannel_Cat,
        -- Campaign costs from finance data
        SUM(fp.LoyaltyRewards) AS loyalty_rewards_costs,
        SUM(fp.Scanback) AS scanback_costs,
        SUM(fp.Total_Discounts) AS total_discount_costs,
        CURRENT_TIMESTAMP() AS data_extraction_timestamp
    FROM `gcp-wow-ent-im-tbl-prod.gs_bigw_fin_data.fin_bigw_profit_v` fp
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_date` dd 
        ON fp.Calendar_Day = dd.CalendarDay
    LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_business_category` bd
        ON UPPER(bd.SubCategory) = UPPER(fp.Category_Description)
    WHERE fp.SalesOrg IN ('1060')
      AND fp.Calendar_Day BETWEEN '2023-06-26' AND CURRENT_DATE()
      AND fp.MerchandiseManager_Code NOT IN ('MM922_AU', 'MM003_AU')
      AND fp.Category_Description != 'CIGARETTES'
      AND fp.Value_Type_Description = 'Actuals'
      -- Filter for campaign-related costs
      AND (fp.LoyaltyRewards > 0 OR fp.Scanback > 0 OR fp.Category_Description = 'Edr Promo Discount')
    GROUP BY 1,2,3,4,5,6,7,8,9,10,11
);

-- =====================================================================================
-- STEP 4: EXTRACT EVERYDAY EXTRA DATA
-- =====================================================================================

-- Extract and process Everyday Extra offer details
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.everyday_extra_details` AS (
    WITH everyday_extra_raw AS (
        SELECT 
            *, 
            -- Standardize order ID format
            IF(channel = 'Online', SUBSTR(edx.OrderID, 5), edx.OrderID) AS OrderId_standardized,
            GENERATE_UUID() AS unique_id
        FROM `gcp-wow-rwds-ai-subs-prod.EDX.EDX_offer_details` edx
        WHERE edx.FiscalWeekStartDate >= '2023-06-26'
          AND edx.banner IN ('Big W')
          AND edx.LoyaltyCustomerTypeDescription IN ('Customer', 'Staff')
    )
    
    SELECT
        edx.crn,
        edx.Banner,
        edx.FiscalWeekStartDate,
        edx.LoyaltyCustomerTypeDescription,
        edx.offer_type,
        edx.benefit,
        edx.channel,
        edx.OrderId_standardized,
        edx.basketkey,
        edx.ordervalue,
        edx.reward_value,
        edx.unique_id,
        dd.FiscalYear,
        dd.FiscalWeekYear,
        dd.FiscalWeek,
        CASE 
            WHEN edx.offer_type IN ('10% BigW', '10% BigW Online') THEN '10% Discount'
            WHEN edx.offer_type LIKE '%3x%' THEN '3x Points'
            WHEN edx.offer_type LIKE '%2x%' THEN '2x Points'
            ELSE edx.offer_type 
        END AS offer_type_category,
        CASE
            WHEN edx.LoyaltyCustomerTypeDescription = 'Staff' THEN 'Team'
            ELSE 'Subscriber'
        END AS customer_type,
        CURRENT_TIMESTAMP() AS data_extraction_timestamp
    FROM everyday_extra_raw edx
    INNER JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_date` dd
        ON edx.FiscalWeekStartDate = dd.FiscalWeekStartDate
);

-- Process Everyday Extra costs at the business/category level
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.everyday_extra_costs` AS (
    -- First get EDX 10% discount baskets
    WITH edx_10_baskets AS (
        SELECT 
            crn,
            basketkey AS basket_key,
            OrderId_standardized AS Basket_OrderID,
            customer_type,
            offer_type_category, 
            SUM(reward_value) AS reward_value
        FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.everyday_extra_details`
        WHERE offer_type_category = '10% Discount'
        GROUP BY 1, 2, 3, 4, 5
    ),
    
    -- Get sales data for baskets with EDX offers
    basket_sales AS (
        SELECT 
            bas.start_txn_date, 
            bd.Business, 
            bd.Category, 
            bas.crn, 
            bas.basket_key,
            bas.order_id AS Basket_OrderID,
            dd.FiscalYear, 
            dd.FiscalWeekYear, 
            dd.FiscalWeek, 
            dd.FiscalWeekStartDate, 
            SUM(bas.tot_amt_incld_gst) AS total_sales,
            COUNT(DISTINCT bas.prod_nbr) AS item_count
        FROM `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.bi_article_sales_bigw` bas  
        LEFT JOIN `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_article_master_v` art
            ON bas.prod_nbr = art.ArticleWITHUOM AND bas.division_nbr = art.SalesOrg
        LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_business_category` bd
            ON bd.SubCategory = INITCAP(art.CategoryDescription)
        INNER JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_date` dd 
            ON bas.start_txn_date = dd.CalendarDay
        WHERE bas.category <> 'Gift Cards'
          AND bas.tot_amt_incld_gst > 0
          AND bas.division_nbr = 1060
          AND dd.FiscalYear IN (2024, 2025)
          -- Only include baskets with EDX orders
          AND bas.order_id IN (SELECT Basket_OrderID FROM edx_10_baskets)
        GROUP BY 1,2,3,4,5,6,7,8,9,10
    ),
    
    -- Link baskets with EDX rewards and calculate distribution
    basket_costs_distribution AS (
        SELECT 
            bs.*, 
            eb.reward_value,
            eb.customer_type,
            SUM(bs.total_sales) OVER (PARTITION BY bs.Basket_OrderID) AS total_sales_basket,
            -- Calculate the distribution percentage for each category in the basket
            SAFE_DIVIDE(bs.total_sales, SUM(bs.total_sales) OVER (PARTITION BY bs.Basket_OrderID)) AS distrib_percent,
            -- Distribute the reward value proportionally to each category
            eb.reward_value * SAFE_DIVIDE(bs.total_sales, SUM(bs.total_sales) OVER (PARTITION BY bs.Basket_OrderID)) AS reward_value_distrib
        FROM basket_sales bs
        INNER JOIN edx_10_baskets eb
            ON bs.Basket_OrderID = eb.Basket_OrderID
            AND bs.crn = eb.crn
    ),
    
    -- Aggregate the EDX costs by time, business, category, and customer type
    edx_costs_aggregated AS (
        SELECT
            FiscalYear,
            FiscalWeekYear,
            FiscalWeek,
            FiscalWeekStartDate,
            Business,
            Category,
            customer_type,
            SUM(reward_value_distrib) AS edx_10pct_cost,
            SUM(total_sales) AS edx_10pct_sales,
            COUNT(DISTINCT Basket_OrderID) AS basket_count,
            CURRENT_TIMESTAMP() AS data_extraction_timestamp
        FROM basket_costs_distribution
        GROUP BY 1,2,3,4,5,6,7
    )
    
    SELECT * FROM edx_costs_aggregated
);

-- Calculate Everyday Extra forecast based on historical patterns and sales forecast
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.everyday_extra_forecast` AS (
    -- Calculate historical EDX cost rates
    WITH edx_historical_rates AS (
        SELECT 
            Business,
            Category,
            customer_type,
            FiscalWeekNo,
            AVG(SAFE_DIVIDE(edx_10pct_cost, edx_10pct_sales)) AS edx_cost_rate,
            AVG(edx_10pct_sales) AS avg_edx_sales
        FROM (
            SELECT 
                Business,
                Category,
                customer_type,
                FiscalWeek AS FiscalWeekNo,
                edx_10pct_cost,
                edx_10pct_sales
            FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.everyday_extra_costs`
            WHERE FiscalYear = 2024 -- Use FY24 as the baseline
        )
        GROUP BY 1,2,3,4
    ),
    
    -- Apply EDX rates to forecasted sales
    edx_forecast_base AS (
        SELECT 
            f.FiscalYear,
            f.FiscalWeekYear,
            f.FiscalWeek,
            f.FiscalWeekStartDate,
            f.Business,
            f.Category,
            f.Net_Sales AS sales_forecast,
            ehr.customer_type,
            ehr.edx_cost_rate,
            -- Apply historical rate to forecast sales with adjustments
            -- Subscriber rate: 10% discount actual rate
            -- Team Member rate: 10% discount actual rate
            CASE 
                WHEN ehr.customer_type = 'Subscriber' THEN f.Net_Sales * COALESCE(ehr.edx_cost_rate, 0) * 1.15 -- 15% growth factor
                WHEN ehr.customer_type = 'Team' THEN f.Net_Sales * COALESCE(ehr.edx_cost_rate, 0) * 1.04 -- 4% growth factor
                ELSE 0
            END AS edx_10pct_cost_forecast,
            CURRENT_TIMESTAMP() AS data_extraction_timestamp
        FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.finance_mapped` f
        LEFT JOIN edx_historical_rates ehr
            ON f.Business = ehr.Business
            AND f.Category = ehr.Category
            AND f.FiscalWeek = ehr.FiscalWeekNo
        WHERE f.DataType = 'Forecast'
        AND f.FiscalYear IN (2024, 2025)
    )
    
    SELECT * FROM edx_forecast_base
    WHERE edx_10pct_cost_forecast > 0
);

-- =====================================================================================
-- STEP 5: CREATE FINAL DASHBOARD TABLES
-- =====================================================================================

-- Create the final dashboard data table combining all elements
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_data` AS (
    -- First get the last date with actual data
    WITH last_actual_date AS (
        SELECT 
            MAX(CalendarDay) AS last_actual_date
        FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.finance_mapped`
        WHERE DataType = 'Actual'
          AND Net_Sales > 0
    ),
    
    -- Combine actuals and forecasts with campaign costs
    combined_data AS (
        SELECT 
            hdc.CalendarDay,
            hdc.FiscalYear,
            hdc.FiscalWeekYear,
            hdc.FiscalWeek,
            hdc.FiscalWeekStartDate,
            hdc.FiscalWeekEndDate,
            hdc.Business,
            hdc.Category,
            -- Financial metrics
            COALESCE(fm.Sales_InclGST, 0) AS Sales_InclGST_Actual,
            COALESCE(fm.Net_Sales, 0) AS Net_Sales_Actual,
            -- Use forecast or actual based on the date
            CASE 
                WHEN hdc.CalendarDay <= (SELECT last_actual_date FROM last_actual_date) 
                    THEN COALESCE(fm.Net_Sales, 0)
                ELSE COALESCE(ff.Net_Sales, 0) 
            END AS Net_Sales,
            -- Campaign costs - actuals and forecast
            COALESCE(ca.loyalty_rewards_costs, 0) AS loyalty_rewards_costs_actual,
            COALESCE(ca.scanback_costs, 0) AS scanback_costs_actual,
            COALESCE(ca.total_discount_costs, 0) AS discount_costs_actual,
            -- Campaign costs forecast
            COALESCE(cf.cost_50bps_forecast_daily, 0) AS campaign_costs_forecast_50bps,
            COALESCE(cf.cost_70bps_forecast_daily, 0) AS campaign_costs_forecast_70bps,
            -- EDX costs - actual and forecast
            COALESCE(SUM(ec.edx_10pct_cost), 0) AS edx_10pct_costs_actual,
            -- EDX forecast
            COALESCE(SUM(ef.edx_10pct_cost_forecast), 0) AS edx_10pct_costs_forecast,
            -- Actual vs Forecast flag
            CASE 
                WHEN hdc.CalendarDay <= (SELECT last_actual_date FROM last_actual_date) 
                    THEN 'Actual'
                ELSE 'Forecast' 
            END AS Data_Type,
            -- Fiscal period for rollups
            CONCAT(CAST(hdc.FiscalYear AS STRING), RIGHT(CONCAT('0000', CAST(dd.BigWFiscalYearPeriod AS STRING)),3)) AS Fiscal_Period,
            -- Add campaign streams if applicable
            STRING_AGG(DISTINCT cf.campaignStream, ', ') AS campaign_streams,
            -- Add metadata
            CURRENT_TIMESTAMP() AS data_extraction_timestamp
        FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.helper_dimension_combinations` hdc
        LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dim_date` dd
            ON hdc.CalendarDay = dd.CalendarDay
        -- Join with finance actuals
        LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.finance_mapped` fm
            ON hdc.CalendarDay = dd.CalendarDay
            AND hdc.Business = fm.Business
            AND hdc.Category = fm.Category
            AND fm.DataType = 'Actual'
        -- Join with finance forecast
        LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.finance_mapped` ff
            ON hdc.CalendarDay = dd.CalendarDay
            AND hdc.Business = ff.Business
            AND hdc.Category = ff.Category
            AND ff.DataType = 'Forecast'
        -- Join with campaign actuals
        LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.campaign_costs_actuals` ca
            ON hdc.CalendarDay = ca.CalendarDay
            AND hdc.Business = ca.Business
            AND hdc.Category = ca.Category
        -- Join with campaign forecast
        LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.campaign_costs_forecast_daily` cf
            ON hdc.CalendarDay = cf.CalendarDay
            AND hdc.Business = cf.Business
            AND hdc.Category = cf.Category
        -- Join with EDX actuals
        LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.everyday_extra_costs` ec
            ON hdc.FiscalWeekYear = ec.FiscalWeekYear
            AND hdc.Business = ec.Business
            AND hdc.Category = ec.Category
        -- Join with EDX forecast
        LEFT JOIN `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.everyday_extra_forecast` ef
            ON hdc.FiscalWeekYear = ef.FiscalWeekYear
            AND hdc.Business = ef.Business
            AND hdc.Category = ef.Category
        GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19
    )
    
    SELECT 
        *,
        -- Calculate total loyalty costs (actual or forecast)
        CASE 
            WHEN Data_Type = 'Actual' THEN 
                loyalty_rewards_costs_actual + scanback_costs_actual + edx_10pct_costs_actual
            ELSE 
                CASE
                    -- For the preferred forecast version, use 50bps
                    WHEN FiscalYear = 2025 THEN campaign_costs_forecast_50bps + edx_10pct_costs_forecast
                    ELSE campaign_costs_forecast_70bps + edx_10pct_costs_forecast
                END
        END AS total_loyalty_costs,
        -- Calculate loyalty costs as % of sales
        SAFE_DIVIDE(
            CASE 
                WHEN Data_Type = 'Actual' THEN 
                    loyalty_rewards_costs_actual + scanback_costs_actual + edx_10pct_costs_actual
                ELSE 
                    CASE
                        WHEN FiscalYear = 2025 THEN campaign_costs_forecast_50bps + edx_10pct_costs_forecast
                        ELSE campaign_costs_forecast_70bps + edx_10pct_costs_forecast
                    END
            END,
            Net_Sales
        ) * 100 AS loyalty_costs_pct_of_sales
    FROM combined_data
    ORDER BY CalendarDay, Business, Category
);

-- Create aggregated summary views for the dashboard
-- Daily summary
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_summary_daily` AS (
    SELECT 
        CalendarDay,
        FiscalYear,
        FiscalWeekYear,
        FiscalWeek,
        FiscalWeekStartDate,
        FiscalWeekEndDate,
        Fiscal_Period,
        Data_Type,
        SUM(Net_Sales) AS Net_Sales,
        SUM(loyalty_rewards_costs_actual) AS loyalty_rewards_costs_actual,
        SUM(scanback_costs_actual) AS scanback_costs_actual,
        SUM(edx_10pct_costs_actual) AS edx_10pct_costs_actual,
        SUM(campaign_costs_forecast_50bps) AS campaign_costs_forecast_50bps,
        SUM(campaign_costs_forecast_70bps) AS campaign_costs_forecast_70bps,
        SUM(edx_10pct_costs_forecast) AS edx_10pct_costs_forecast,
        SUM(total_loyalty_costs) AS total_loyalty_costs,
        SAFE_DIVIDE(SUM(total_loyalty_costs), SUM(Net_Sales)) * 100 AS loyalty_costs_pct_of_sales,
        data_extraction_timestamp
    FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_data`
    GROUP BY 1,2,3,4,5,6,7,8,19
    ORDER BY CalendarDay
);

-- Weekly summary
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_summary_weekly` AS (
    SELECT 
        FiscalYear,
        FiscalWeekYear,
        FiscalWeek,
        FiscalWeekStartDate,
        FiscalWeekEndDate,
        Fiscal_Period,
        -- For weekly, we need to determine if the week is fully actual, fully forecast, or mixed
        CASE
            WHEN COUNT(DISTINCT Data_Type) > 1 THEN 'Mixed'
            ELSE MAX(Data_Type)
        END AS Data_Type,
        SUM(Net_Sales) AS Net_Sales,
        SUM(loyalty_rewards_costs_actual) AS loyalty_rewards_costs_actual,
        SUM(scanback_costs_actual) AS scanback_costs_actual,
        SUM(edx_10pct_costs_actual) AS edx_10pct_costs_actual,
        SUM(campaign_costs_forecast_50bps) AS campaign_costs_forecast_50bps,
        SUM(campaign_costs_forecast_70bps) AS campaign_costs_forecast_70bps,
        SUM(edx_10pct_costs_forecast) AS edx_10pct_costs_forecast,
        SUM(total_loyalty_costs) AS total_loyalty_costs,
        SAFE_DIVIDE(SUM(total_loyalty_costs), SUM(Net_Sales)) * 100 AS loyalty_costs_pct_of_sales,
        data_extraction_timestamp
    FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_data`
    GROUP BY 1,2,3,4,5,6
    ORDER BY FiscalWeekStartDate
);

-- Business summary
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_summary_business` AS (
    SELECT 
        FiscalYear,
        FiscalWeekYear,
        FiscalWeek,
        FiscalWeekStartDate,
        FiscalWeekEndDate,
        Fiscal_Period,
        Business,
        Data_Type,
        SUM(Net_Sales) AS Net_Sales,
        SUM(loyalty_rewards_costs_actual) AS loyalty_rewards_costs_actual,
        SUM(scanback_costs_actual) AS scanback_costs_actual,
        SUM(edx_10pct_costs_actual) AS edx_10pct_costs_actual,
        SUM(campaign_costs_forecast_50bps) AS campaign_costs_forecast_50bps,
        SUM(campaign_costs_forecast_70bps) AS campaign_costs_forecast_70bps,
        SUM(edx_10pct_costs_forecast) AS edx_10pct_costs_forecast,
        SUM(total_loyalty_costs) AS total_loyalty_costs,
        SAFE_DIVIDE(SUM(total_loyalty_costs), SUM(Net_Sales)) * 100 AS loyalty_costs_pct_of_sales,
        data_extraction_timestamp
    FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_data`
    GROUP BY 1,2,3,4,5,6,7,8
    ORDER BY FiscalWeekStartDate, Business
);

-- Period summary for quarterly/monthly views
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_summary_period` AS (
    SELECT 
        FiscalYear,
        Fiscal_Period,
        CASE
            WHEN COUNT(DISTINCT Data_Type) > 1 THEN 'Mixed'
            ELSE MAX(Data_Type)
        END AS Data_Type,
        SUM(Net_Sales) AS Net_Sales,
        SUM(loyalty_rewards_costs_actual) AS loyalty_rewards_costs_actual,
        SUM(scanback_costs_actual) AS scanback_costs_actual,
        SUM(edx_10pct_costs_actual) AS edx_10pct_costs_actual,
        SUM(campaign_costs_forecast_50bps) AS campaign_costs_forecast_50bps,
        SUM(campaign_costs_forecast_70bps) AS campaign_costs_forecast_70bps,
        SUM(edx_10pct_costs_forecast) AS edx_10pct_costs_forecast,
        SUM(total_loyalty_costs) AS total_loyalty_costs,
        SAFE_DIVIDE(SUM(total_loyalty_costs), SUM(Net_Sales)) * 100 AS loyalty_costs_pct_of_sales,
        data_extraction_timestamp
    FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_data`
    GROUP BY 1,2
    ORDER BY FiscalYear, Fiscal_Period
);

-- Annual summary
CREATE OR REPLACE TABLE `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_summary_annual` AS (
    SELECT 
        FiscalYear,
        CASE
            WHEN COUNT(DISTINCT Data_Type) > 1 THEN 'Mixed'
            ELSE MAX(Data_Type)
        END AS Data_Type,
        SUM(Net_Sales) AS Net_Sales,
        SUM(loyalty_rewards_costs_actual) AS loyalty_rewards_costs_actual,
        SUM(scanback_costs_actual) AS scanback_costs_actual,
        SUM(edx_10pct_costs_actual) AS edx_10pct_costs_actual,
        SUM(campaign_costs_forecast_50bps) AS campaign_costs_forecast_50bps,
        SUM(campaign_costs_forecast_70bps) AS campaign_costs_forecast_70bps,
        SUM(edx_10pct_costs_forecast) AS edx_10pct_costs_forecast,
        SUM(total_loyalty_costs) AS total_loyalty_costs,
        SAFE_DIVIDE(SUM(total_loyalty_costs), SUM(Net_Sales)) * 100 AS loyalty_costs_pct_of_sales,
        data_extraction_timestamp
    FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_data`
    GROUP BY 1
    ORDER BY FiscalYear
);

-- Create a view for dashboard users to easily access the data
CREATE OR REPLACE VIEW `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_view` AS (
    SELECT * FROM `gcp-wow-rwds-ai-pobe-dev.points_cost_forecast.dashboard_data`
);

/*
 * Points Cost Forecast Production Script - Complete
 * This script created a comprehensive set of tables to power the Points Cost Forecast dashboard.
 * 
 * Key tables created:
 * - dim_date: Calendar dimensions
 * - dim_business_category: Business/category mapping
 * - finance_mapped: Actual and forecasted financial data
 * - campaign_costs_forecast: Campaign forecasted costs
 * - campaign_costs_actuals: Campaign actual costs
 * - everyday_extra_costs: Everyday Extra actual costs
 * - everyday_extra_forecast: Everyday Extra forecasted costs
 * - dashboard_data: Complete dataset combining actuals and forecasts
 * - dashboard_summary_*: Aggregated views at various levels (daily, weekly, business, period, annual)
 * 
 * Use the dashboard_view for easy access to the data.
 */