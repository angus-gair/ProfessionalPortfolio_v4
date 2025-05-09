# Points Cost Forecast: Project Overview

## Executive Summary

The Points Cost Forecast system provides BigW with a comprehensive solution for tracking, analyzing, and forecasting loyalty program costs across different business categories. This system enables accurate comparison between forecasted and actual costs, helping stakeholders make data-driven decisions about marketing campaigns and loyalty initiatives.

![Weekly Dashboard View](../dashboard%20screenshot.pdf)

## Business Value

- **Financial Planning**: Accurately forecast loyalty costs and evaluate against actuals
- **Marketing Optimization**: Analyze campaign performance and ROI by business/category
- **Performance Monitoring**: Track loyalty costs as a percentage of sales across time periods
- **Cost Allocation**: Distribute loyalty costs to appropriate business units
- **Decision Support**: Enable data-driven decisions about future campaigns and promotions

## Key Components

### Data Sources
1. **Finance System**: Financial actuals and forecasts from BigW Finance
2. **Loyalty Analytics**: Article-level sales data 
3. **Everyday Extra**: EDX offer details and rewards
4. **Business Mapping**: Business/category hierarchies
5. **Campaign Details**: Campaign plans and budget allocations

### Core Processes
1. **ETL Pipeline**: Transforms raw data into actionable insights
2. **Cost Forecasting**: Projects future loyalty costs based on budget allocations
3. **Business Mapping**: Aligns costs with business categories
4. **Cost Distribution**: Distributes costs down to daily granularity
5. **Dashboard Integration**: Powers visualizations for stakeholders

### Output Dashboards
1. **Executive Summary**: High-level KPIs and trends
2. **Time Series Analysis**: Trends across fiscal periods
3. **Business Breakdown**: Costs by business category
4. **Campaign Performance**: Analysis by campaign stream
5. **Forecast vs Actual**: Variance analysis

## Visual Project Documentation

For a comprehensive understanding of the project, please refer to the following visual documentation:

1. [High-Level Data Flow Diagram](./1_High_Level_Data_Flow_Diagram.md) - Overview of the system data flow
2. [Data Model Diagram](./2_Data_Model_Diagram.md) - Table structures and relationships
3. [SQL Execution Flow](./3_SQL_Execution_Flow.md) - Step-by-step process of the ETL pipeline
4. [Technical Table Relationships](./4_Technical_Table_Relationships.md) - Detailed join logic for developers
5. [Dashboard Visualization Mockup](./5_Dashboard_Visualization_Mockup.md) - Preview of dashboard interfaces

## Technical Implementation

The Points Cost Forecast system is implemented as a series of BigQuery SQL scripts organized into five main stages:

1. **Create Common Dimension Tables**: Establish reference tables for time, business categorization, and weighting factors
2. **Extract Finance Data**: Process actual and forecasted financials with business/category mapping
3. **Process Campaign Costs**: Calculate campaign cost distributions and forecasts
4. **Extract Everyday Extra Data**: Process Everyday Extra loyalty program costs
5. **Create Dashboard Tables**: Combine all metrics into unified dashboard views

### Key SQL Logic

The core transformations include:

```sql
-- Campaign cost forecast calculation using basis points
cd.costs_budget_fcast * 0.0050 AS cost_50bps_forecast

-- EDX cost distribution across categories
eb.reward_value * SAFE_DIVIDE(bs.total_sales, SUM(bs.total_sales) OVER (PARTITION BY bs.Basket_OrderID)) AS reward_value_distrib

-- Total loyalty costs calculation
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

## Production Schedule

The Points Cost Forecast system follows this operational schedule:

1. **Daily Refresh**: Incremental updates for actuals data
2. **Weekly Full Refresh**: Complete data processing (recommended on Mondays)
3. **Monthly Forecast Updates**: When campaign plans or budgets change
4. **Quarterly Review**: Comprehensive analysis of forecast accuracy

## Related Documentation

For additional details, please refer to these resources:

- [Points Cost Forecast Dashboard User Guide](../Points_Cost_Forecast_Dashboard_User_Guide.md)
- [Business Destination Mapping Reference](../Business_Destination_Mapping_Reference.md)
- [Campaign Planning Guide](../Campaign_Planning_Guide.md)
- [Fiscal Calendar Reference](../Fiscal_Calendar_Reference.md)
- [Points Cost Forecast Technical Documentation](../Points_Cost_Forecast_Technical_Documentation.md)
- [Points Cost Forecast Production SQL](../Points_Cost_Forecast_Production.sql)

---

*Document Version: 1.0*  
*Last Updated: May 9, 2025*
