# Points Cost Forecast: Technical Documentation

## 1. Overview

This document provides technical documentation for the Points Cost Forecast production SQL script, a comprehensive solution designed to compare forecasted budget costs against actual incurred costs at multiple levels of business granularity. The system supports business decision-making by highlighting variances and trends at both business/category level and down to individual campaign streams.

### 1.1 Purpose

The Points Cost Forecast dashboard provides stakeholders with:

- Comparison of actual vs. forecasted loyalty costs
- Multi-level analysis (daily, weekly, monthly, quarterly, annual)
- Business and category breakdowns
- Campaign-specific cost tracking
- Everyday Extra program cost analysis

### 1.2 Architecture

The solution follows a modular ETL (Extract, Transform, Load) architecture:

1. **Extract**: Data is sourced from multiple BigQuery tables including finance, sales, and campaign systems
2. **Transform**: A series of SQL transformations clean, join, and aggregate the data
3. **Load**: Final tables are created to power dashboard visualizations

## 2. Data Sources

The system integrates data from multiple sources:

| Source | Description | Table Path | Key Fields |
|--------|-------------|------------|------------|
| Finance System | Financial actuals and forecasts | `gcp-wow-ent-im-tbl-prod.gs_bigw_fin_data.fin_bigw_profit_v` | Sales_InclTax, Sales_ExclTax, Scanback, LoyaltyRewards |
| Loyalty Analytics | Article-level sales data | `gcp-wow-rwds-ai-data-prod.loyalty_bi_analytics.bi_article_sales_bigw` | tot_amt_incld_gst, tot_amt_excld_gst_wt_wow |
| Everyday Extra | EDX offer details | `gcp-wow-rwds-ai-subs-prod.EDX.EDX_offer_details` | offer_type, reward_value, ordervalue |
| Business Mapping | Business/category hierarchy | `gcp-wow-rwds-ai-data-prod.outbound.BigW_Destination_Business` | Business, Category, SubCategory |
| Campaign Details | Campaign forecasts | `gcp-wow-rwds-ai-pobe-dev.angus.bigw_campaign_details_planOnPage_FY25_PART2_static` | campaignStream, costs_budget_fcast |
| Calendar Dimensions | Date and fiscal period mapping | `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_masterdata_view.dim_date_v` | FiscalYear, FiscalWeek, FiscalWeekStartDate |

## 3. Data Model

### 3.1 Dimension Tables

- **dim_date**: Calendar dimensions including fiscal year/week mapping
- **dim_business_category**: Business and category hierarchies
- **dim_day_of_week_weights**: Weighting factors to distribute weekly values to daily granularity

### 3.2 Fact Tables

- **finance_actuals**: Actual financial metrics extracted from the finance system
- **finance_forecast**: Forecasted financial metrics
- **finance_mapped**: Combined actuals and forecasts mapped to business/category dimensions
- **article_sales_actuals**: Granular article-level sales data
- **campaign_costs_forecast**: Forecasted campaign costs
- **campaign_costs_actuals**: Actual campaign costs
- **everyday_extra_costs**: Everyday Extra program actual costs
- **everyday_extra_forecast**: Forecasted Everyday Extra costs

### 3.3 Dashboard Tables

- **dashboard_data**: Complete dataset joining all metrics
- **dashboard_summary_daily**: Daily aggregated view
- **dashboard_summary_weekly**: Weekly aggregated view
- **dashboard_summary_business**: Business-level view
- **dashboard_summary_period**: Period (monthly/quarterly) view
- **dashboard_summary_annual**: Annual summary

## 4. ETL Process

The ETL process consists of five major steps:

### 4.1 Create Common Dimension Tables

Dimension tables provide the foundation for all subsequent analysis, including:

- Calendar dimensions (fiscal years, weeks, periods)
- Business/category mapping
- Day-of-week weightings for distributing values

### 4.2 Extract Finance Actuals and Forecasts

This step processes financial data:

- Extracts actuals from the finance system
- Extracts forecasts for future periods
- Maps finance data to business/category dimensions
- Processes article-level sales for granular analysis

### 4.3 Process Campaign Costs and Forecasts

Campaign processing includes:

- Extracting campaign details and stream structures
- Calculating campaign cost forecasts based on budget allocations
- Distributing campaign costs across business/category dimensions
- Creating daily forecast distributions for campaign costs
- Extracting campaign cost actuals from the finance system

### 4.4 Extract Everyday Extra Data

Everyday Extra program analysis includes:

- Processing EDX offer details
- Calculating actual costs at business/category level
- Creating forecasts based on historical patterns
- Applying growth factors for team and subscriber segments

### 4.5 Create Final Dashboard Tables

Final dashboard tables combine all metrics:

- Creating a comprehensive dataset with actuals and forecasts
- Calculating total loyalty costs
- Creating aggregated views at different granularity levels
- Setting up a view for dashboard users

## 5. Key Calculations

### 5.1 Campaign Cost Forecasts

Campaign costs are forecasted using tiered basis point calculations:

```sql
cd.costs_budget_fcast * 0.0050 AS cost_50bps_forecast,
cd.costs_budget_fcast * 0.0020 AS cost_20bps_forecast,
cd.costs_budget_fcast * 0.0070 AS cost_70bps_forecast
```

### 5.2 Everyday Extra Cost Distribution

EDX costs are distributed across categories proportional to sales:

```sql
SAFE_DIVIDE(bs.total_sales, SUM(bs.total_sales) OVER (PARTITION BY bs.Basket_OrderID)) AS distrib_percent,
eb.reward_value * SAFE_DIVIDE(bs.total_sales, SUM(bs.total_sales) OVER (PARTITION BY bs.Basket_OrderID)) AS reward_value_distrib
```

### 5.3 Total Loyalty Costs

Total loyalty costs combine multiple sources based on data type:

```sql
CASE 
    WHEN Data_Type = 'Actual' THEN 
        loyalty_rewards_costs_actual + scanback_costs_actual + edx_10pct_costs_actual
    ELSE 
        CASE
            WHEN FiscalYear = 2025 THEN campaign_costs_forecast_50bps + edx_10pct_costs_forecast
            ELSE campaign_costs_forecast_70bps + edx_10pct_costs_forecast
        END
END AS total_loyalty_costs
```

## 6. Performance Considerations

### 6.1 Query Optimization

The script incorporates several optimization techniques:

- **Filtered JOINs**: Only joining on necessary conditions
- **Partitioning**: Using fiscal periods for efficient data slicing
- **Selective Columns**: Only selecting required fields
- **COALESCE**: Handling NULL values efficiently
- **Intermediate Tables**: Breaking complex logic into manageable CTEs

### 6.2 Resource Utilization

Resource considerations include:

- Largest tables (~5-10GB): dashboard_data, article_sales_actuals
- High compute operations: Cross joins with business/category dimensions
- Recommended refresh cycle: Daily, with incremental updates

### 6.3 Execution Plan

The script execution follows a logical dependency path:

1. Dimension tables must be created first
2. Fact tables can be processed in parallel
3. Final dashboard tables must be created last

## 7. Maintenance and Operations

### 7.1 Refresh Schedule

- **Full refresh**: Weekly (recommended on Mondays)
- **Incremental updates**: Daily for actuals
- **Forecast updates**: Monthly or when campaign plans change

### 7.2 Monitoring

Key monitoring points:

- **Data freshness**: Check finance_actuals.data_extraction_timestamp
- **Data completeness**: Monitor row counts in dashboard_data
- **Execution time**: Typical full refresh ~30-45 minutes

### 7.3 Troubleshooting

Common issues and resolution steps:

- **Missing business mapping**: Update dim_business_category
- **Forecast accuracy**: Check costs_budget_fcast values
- **EDX allocation issues**: Verify reward_value_distrib calculation

## 8. Future Enhancements

Potential improvements to consider:

- Machine learning for improved forecast accuracy
- API integration with BI visualization tools
- Automated anomaly detection for cost variances
- Campaign effectiveness metrics integration

## 9. Appendix

### 9.1 Glossary

- **EDX**: Everyday Extra program
- **Scanback**: Loyalty points rewards costs
- **bps**: Basis points (1 bps = 0.01%)
- **FY24/FY25**: Fiscal Year 2024/2025
- **Campaign Stream**: Categorized marketing campaign

### 9.2 Related Documents

- Points Cost Forecast Dashboard User Guide
- Business Destination Mapping Reference
- Campaign Planning Guide
- Fiscal Calendar Reference

---

*Documentation Version: 1.0*  
*Last Updated: May 9, 2025*  
*Author: Cascade AI*
