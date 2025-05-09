# Points Cost Forecast: High-Level Data Flow

```mermaid
flowchart TD
    subgraph "Data Sources"
        A1[Finance System] 
        A2[Loyalty Analytics]
        A3[Campaign Forecasts]
        A4[Everyday Extra Data]
        A5[Business Mapping]
        A6[Calendar Dimensions]
    end

    subgraph "ETL Process"
        B1[1. Create Dimension Tables]
        B2[2. Extract Finance Data]
        B3[3. Process Campaign Costs]
        B4[4. Extract EDX Data]
        B5[5. Create Dashboard Tables]
    end

    subgraph "Dashboard Tables"
        C1[dashboard_data]
        C2[dashboard_summary_daily]
        C3[dashboard_summary_weekly]
        C4[dashboard_summary_business]
        C5[dashboard_summary_period]
        C6[dashboard_summary_annual]
        C7[dashboard_view]
    end

    A1 --> B2
    A2 --> B2
    A3 --> B3
    A4 --> B4
    A5 --> B1
    A6 --> B1

    B1 --> B2
    B1 --> B3
    B1 --> B4
    
    B2 --> B5
    B3 --> B5
    B4 --> B5

    B5 --> C1
    C1 --> C2
    C1 --> C3
    C1 --> C4
    C1 --> C5
    C1 --> C6
    C1 --> C7

    class A1,A2,A3,A4,A5,A6 sourceNode
    class B1,B2,B3,B4,B5 processNode
    class C1,C2,C3,C4,C5,C6,C7 destinationNode

    classDef sourceNode fill:#f9f9f9,stroke:#666,stroke-width:2px
    classDef processNode fill:#d0e0ff,stroke:#0066cc,stroke-width:2px
    classDef destinationNode fill:#d8f0d8,stroke:#006600,stroke-width:2px
```

## Key Components

### Data Sources
- **Finance System**: Financial actuals and forecasts
- **Loyalty Analytics**: Article-level sales data
- **Campaign Forecasts**: Campaign plans and budget allocations
- **Everyday Extra Data**: EDX offer details and rewards
- **Business Mapping**: Business/category hierarchies
- **Calendar Dimensions**: Fiscal mapping and date dimensions

### ETL Process
1. **Create Dimension Tables**: Establish reference tables for time, business categorization, and weighting factors
2. **Extract Finance Data**: Process actual and forecasted financials with business/category mapping
3. **Process Campaign Costs**: Calculate campaign cost distributions and forecasts
4. **Extract EDX Data**: Process Everyday Extra loyalty program costs
5. **Create Dashboard Tables**: Combine all metrics into unified dashboard views

### Dashboard Tables
- **dashboard_data**: Complete dataset with detailed metrics
- **dashboard_summary_daily**: Daily aggregation of costs and sales
- **dashboard_summary_weekly**: Weekly aggregation for trend analysis
- **dashboard_summary_business**: Business-level performance view
- **dashboard_summary_period**: Monthly and quarterly aggregations
- **dashboard_summary_annual**: Annual summary across fiscal years
- **dashboard_view**: Comprehensive view for dashboard users
