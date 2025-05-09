# Points Cost Forecast: Data Model Diagram

```mermaid
erDiagram
    DIM_DATE {
        date CalendarDay PK
        string FiscalWeekYear
        int FiscalWeek
        date FiscalWeekEndDate
        int FiscalYear
        string Fiscal_Period
        date FiscalWeekStartDate
        int BigWFiscalYear
        int BigWFiscalYearPeriod
        int BigWFiscalWeek
        string DayOfWeek
        int WeekDayNumber
    }

    DIM_BUSINESS_CATEGORY {
        string Business
        string Category
        string SubCategory
    }

    DIM_DAY_OF_WEEK_WEIGHTS {
        string DayOfWeek PK
        float daily_weight
    }

    FINANCE_ACTUALS {
        int FiscalYear
        string FiscalWeekYear
        int FiscalWeek
        date FiscalWeekStartDate
        string Fiscal_Period
        string Business_profit_v
        string Category
        string CategoryWithoutCompanyCode
        string Category_Description_profit_v
        string SalesChannel_Cat
        float Sales_InclGST
        float Net_Sales
        float Scanback
        float Total_Discounts_And_Rewards
        float COGS
        float Gross_Profit
        timestamp data_extraction_timestamp
    }

    FINANCE_FORECAST {
        int FiscalYear
        string FiscalWeekYear
        int FiscalWeek
        date FiscalWeekStartDate
        string Fiscal_Period
        string Category_Description_profit_v
        float Sales_InclGST
        float Net_Sales
        float Scanback
        timestamp data_extraction_timestamp
    }

    FINANCE_MAPPED {
        int FiscalYear
        string FiscalWeekYear
        int FiscalWeek
        date FiscalWeekStartDate
        string Fiscal_Period
        string Business
        string Category
        string DataType
        float Net_Sales
        float Scanback
        timestamp data_extraction_timestamp
    }

    ARTICLE_SALES_ACTUALS {
        date start_txn_date
        int FiscalYear
        string FiscalWeekYear
        int FiscalWeek
        date FiscalWeekStartDate
        string Business
        string Category
        float total_sales_incl_gst
        float total_sales_excl_gst
        timestamp data_extraction_timestamp
    }

    CAMPAIGN_DETAILS {
        string campaignStream PK
        string CampaignDetails
        date fw_CampaignStartDate
        date fw_CampaignEndDate
        string CampaignCode
        string CampaignName
        string CampaignCategoryType
        string Include_Categories
        date FiscalWeekStartDate
        float costs_budget_fcast
        int campaign_row_id
    }

    CAMPAIGN_COSTS_FORECAST {
        string campaignStream FK
        string CampaignCategoryType
        date FiscalWeekStartDate
        string FiscalWeekYear
        int FiscalYear
        int FiscalWeek
        string Business
        string Category
        float cost_50bps_forecast
        timestamp data_extraction_timestamp
    }

    CAMPAIGN_COSTS_ACTUALS {
        date CalendarDay
        string campaignStream FK
        string CampaignCategoryType
        int FiscalYear
        string FiscalWeekYear
        int FiscalWeek
        date FiscalWeekStartDate
        string Business
        string Category
        float campaign_costs_daily
        timestamp data_extraction_timestamp
    }

    EVERYDAY_EXTRA_COSTS {
        date CalendarDay
        int FiscalYear
        string FiscalWeekYear
        int FiscalWeek
        date FiscalWeekStartDate
        string Business
        string Category
        float edx_10pct_costs
        timestamp data_extraction_timestamp
    }

    EVERYDAY_EXTRA_FORECAST {
        date CalendarDay
        int FiscalYear
        string FiscalWeekYear
        int FiscalWeek
        date FiscalWeekStartDate
        string Business
        string Category
        float edx_10pct_costs_forecast
        timestamp data_extraction_timestamp
    }

    DASHBOARD_DATA {
        date CalendarDay
        int FiscalYear
        string FiscalWeekYear
        int FiscalWeek
        date FiscalWeekStartDate
        date FiscalWeekEndDate
        string Fiscal_Period
        string Business
        string Category
        string DataType
        float Net_Sales
        float loyalty_rewards_costs_actual
        float scanback_costs_actual
        float edx_10pct_costs_actual
        float campaign_costs_forecast_50bps
        float campaign_costs_forecast_70bps
        float edx_10pct_costs_forecast
        float total_loyalty_costs
        float loyalty_costs_pct_of_sales
        timestamp data_extraction_timestamp
    }

    DIM_DATE ||--o{ FINANCE_ACTUALS : "maps dates"
    DIM_DATE ||--o{ FINANCE_FORECAST : "maps dates"
    DIM_DATE ||--o{ ARTICLE_SALES_ACTUALS : "maps dates"
    DIM_DATE ||--o{ CAMPAIGN_COSTS_FORECAST : "maps dates"
    DIM_DATE ||--o{ CAMPAIGN_COSTS_ACTUALS : "maps dates"
    DIM_DATE ||--o{ EVERYDAY_EXTRA_COSTS : "maps dates"
    DIM_DATE ||--o{ EVERYDAY_EXTRA_FORECAST : "maps dates"
    DIM_DATE ||--o{ DASHBOARD_DATA : "maps dates"

    DIM_BUSINESS_CATEGORY ||--o{ FINANCE_MAPPED : "maps business"
    DIM_BUSINESS_CATEGORY ||--o{ ARTICLE_SALES_ACTUALS : "maps business"
    DIM_BUSINESS_CATEGORY ||--o{ CAMPAIGN_COSTS_FORECAST : "maps business"
    DIM_BUSINESS_CATEGORY ||--o{ CAMPAIGN_COSTS_ACTUALS : "maps business"
    DIM_BUSINESS_CATEGORY ||--o{ EVERYDAY_EXTRA_COSTS : "maps business"
    DIM_BUSINESS_CATEGORY ||--o{ EVERYDAY_EXTRA_FORECAST : "maps business"
    DIM_BUSINESS_CATEGORY ||--o{ DASHBOARD_DATA : "maps business"

    DIM_DAY_OF_WEEK_WEIGHTS ||--o{ CAMPAIGN_COSTS_ACTUALS : "distributes costs"
    DIM_DAY_OF_WEEK_WEIGHTS ||--o{ EVERYDAY_EXTRA_FORECAST : "distributes costs"

    CAMPAIGN_DETAILS ||--o{ CAMPAIGN_COSTS_FORECAST : "forecasts costs"
    CAMPAIGN_DETAILS ||--o{ CAMPAIGN_COSTS_ACTUALS : "maps actuals"

    FINANCE_ACTUALS --o{ FINANCE_MAPPED : "provides actuals"
    FINANCE_FORECAST --o{ FINANCE_MAPPED : "provides forecasts"

    FINANCE_MAPPED --o{ DASHBOARD_DATA : "finance metrics"
    CAMPAIGN_COSTS_FORECAST --o{ DASHBOARD_DATA : "campaign forecasts"
    CAMPAIGN_COSTS_ACTUALS --o{ DASHBOARD_DATA : "campaign actuals"
    EVERYDAY_EXTRA_COSTS --o{ DASHBOARD_DATA : "EDX actuals"
    EVERYDAY_EXTRA_FORECAST --o{ DASHBOARD_DATA : "EDX forecasts"
```

## Table Descriptions

### Dimension Tables
- **DIM_DATE**: Calendar dimensions with fiscal year/week mapping
- **DIM_BUSINESS_CATEGORY**: Business and category hierarchies
- **DIM_DAY_OF_WEEK_WEIGHTS**: Day-of-week weighting factors for cost distribution

### Finance Tables
- **FINANCE_ACTUALS**: Actual financial metrics from finance system
- **FINANCE_FORECAST**: Forecasted financial metrics for future periods
- **FINANCE_MAPPED**: Combined actuals and forecasts mapped to business dimensions
- **ARTICLE_SALES_ACTUALS**: Granular article-level sales data

### Campaign Tables
- **CAMPAIGN_DETAILS**: Campaign metadata and forecast budgets
- **CAMPAIGN_COSTS_FORECAST**: Forecasted campaign costs by business/category
- **CAMPAIGN_COSTS_ACTUALS**: Actual campaign costs distributed daily

### Everyday Extra Tables
- **EVERYDAY_EXTRA_COSTS**: Actual EDX program costs
- **EVERYDAY_EXTRA_FORECAST**: Forecasted EDX program costs

### Dashboard Table
- **DASHBOARD_DATA**: Complete dataset combining all metrics
  - Feeds into various summary tables (daily, weekly, business, period, annual)
  - Exposed as dashboard_view for reporting
