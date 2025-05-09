# Points Cost Forecast: Dashboard Visualization Mockup

## Executive Dashboard

```mermaid
graph TD
    subgraph "Points Cost Forecast Dashboard"
        subgraph "KPI Summary"
            KPI1["Total Loyalty Costs<br/>$52.3M"]
            KPI2["% of Net Sales<br/>2.78%"]
            KPI3["YoY Change<br/>+0.32%"]
            KPI4["Forecast Accuracy<br/>97.8%"]
        end
        
        subgraph "Time Series Trends"
            TS1["Weekly Points Cost Trend<br/><small>Line chart showing actual vs forecast</small>"]
        end
        
        subgraph "Business Breakdown"
            BB1["Points Cost by Business<br/><small>Bar chart by business</small>"]
        end
        
        subgraph "Campaign Analysis"
            CA1["Top Campaign Streams<br/><small>Cost breakdown by campaign</small>"]
        end
        
        subgraph "EDX Performance"
            EDX1["EDX Cost Trend<br/><small>Line chart of EDX costs</small>"]
        end
    end
```

## Weekly View Dashboard

![Weekly Dashboard View](../dashboard%20screenshot.pdf)

## Business Category View

The dashboard provides drill-down capabilities from Business to Category level:

```mermaid
graph TD
    subgraph "Business Category Drilldown"
        BD1["General Merchandise<br/>$12.5M"]
        BD2["Home<br/>$9.2M"]
        BD3["Entertainment<br/>$8.7M"]
        BD4["Apparel<br/>$6.8M"]
        BD5["Toys & Baby<br/>$6.1M"]
        BD6["Seasonal<br/>$5.2M"]
        BD7["Other<br/>$3.8M"]
        
        BD1 --> BD1_1["Kitchenware<br/>$4.2M"]
        BD1 --> BD1_2["Storage<br/>$3.1M"]
        BD1 --> BD1_3["Small Appliances<br/>$2.8M"]
        BD1 --> BD1_4["Other GM<br/>$2.4M"]
        
        BD2 --> BD2_1["Furniture<br/>$3.5M"]
        BD2 --> BD2_2["Bedding<br/>$2.9M"]
        BD2 --> BD2_3["Other Home<br/>$2.8M"]
    end
```

## Campaign Analysis View

Campaign Stream analysis provides detailed performance metrics:

| Campaign Stream | Budget Forecast | 50bps Forecast | Actual Cost | Variance | 
|----------------|----------------|----------------|-------------|----------|
| Homewares | $24.8M | $1.24M | $1.21M | -2.4% |
| Back to School | $18.2M | $0.91M | $0.95M | +4.4% |
| Toy Sale | $32.5M | $1.63M | $1.72M | +5.5% |
| Electronics | $15.6M | $0.78M | $0.74M | -5.1% |
| Seasonal | $21.9M | $1.10M | $1.08M | -1.8% |

## Dashboard Filters

The dashboard supports multiple filters to analyze data:

- **Date Range**: Select custom date ranges or preset periods (This Year, Last Year, YTD)
- **Fiscal Hierarchy**: Filter by Fiscal Year, Period, or Week
- **Business Hierarchy**: Filter by Business, Category, or Subcategory
- **Campaign Stream**: Filter by specific marketing campaigns
- **Data Type**: Toggle between Actual, Forecast, or Combined view

## Time Series Comparison

![Aggregated Dashboard View](../dashboard%20screenshot%20aggregated.pdf)

## Key Metrics Explained

1. **Total Loyalty Costs**: Sum of all loyalty program costs:
   - Campaign Costs (50bps/70bps of sales)
   - Scanback Costs
   - EDX 10% Program Costs

2. **Loyalty Costs % of Sales**: Total loyalty costs divided by net sales

3. **Forecast vs Actual Variance**: Difference between forecasted and actual costs
   - Positive: Actual costs higher than forecast
   - Negative: Actual costs lower than forecast

4. **YoY Comparison**: Current year vs. previous year comparison
   - Absolute change in dollars
   - Percentage change in loyalty costs % of sales

## Dashboard Navigation Guide

1. Start at the **Executive Summary** for high-level KPIs
2. Explore the **Time Series Trends** to identify patterns
3. Use the **Business Breakdown** to drill into specific business areas
4. Analyze **Campaign Performance** to evaluate marketing effectiveness
5. Review **EDX Performance** to understand subscription program costs
6. Apply **Filters** to focus on areas of interest
7. Export data using the dashboard **Download** options
