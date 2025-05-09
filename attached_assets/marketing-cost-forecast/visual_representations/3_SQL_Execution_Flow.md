# Points Cost Forecast: SQL Execution Flow

```mermaid
graph TD
    subgraph "Step 1: Create Common Dimension Tables"
        A1[Create dim_date]
        A2[Create dim_business_category]
        A3[Create dim_day_of_week_weights]
    end

    subgraph "Step 2: Extract Finance Data"
        B1[Create finance_actuals]
        B2[Create finance_forecast]
        B3[Create finance_mapped]
        B4[Create article_sales_actuals]
        B5[Create helper_dimension_combinations]
    end

    subgraph "Step 3: Process Campaign Costs"
        C1[Create campaign_details]
        C2[Create campaign_costs_forecast]
        C3[Create campaign_costs_actuals]
    end

    subgraph "Step 4: Extract EDX Data"
        D1[Create everyday_extra_costs]
        D2[Create everyday_extra_forecast]
    end

    subgraph "Step 5: Create Dashboard Tables"
        E1[Create dashboard_data]
        E2[Create dashboard_summary_daily]
        E3[Create dashboard_summary_weekly]
        E4[Create dashboard_summary_business]
        E5[Create dashboard_summary_period]
        E6[Create dashboard_summary_annual]
        E7[Create dashboard_view]
    end

    A1 --> B1
    A1 --> B2
    A1 --> B4
    A1 --> B5
    A1 --> C2
    A1 --> C3
    A1 --> D1
    A1 --> D2
    A1 --> E1

    A2 --> B3
    A2 --> B4
    A2 --> C2
    A2 --> C3
    A2 --> D1
    A2 --> D2
    A2 --> E1

    A3 --> C3
    A3 --> D2

    B1 --> B3
    B2 --> B3
    B3 --> E1
    B4 --> E1
    B5 --> E1

    C1 --> C2
    C1 --> C3
    C2 --> E1
    C3 --> E1

    D1 --> E1
    D2 --> E1

    E1 --> E2
    E1 --> E3
    E1 --> E4
    E1 --> E5
    E1 --> E6
    E1 --> E7

    classDef step1 fill:#f9d5e5,stroke:#333,stroke-width:1px
    classDef step2 fill:#eeeeee,stroke:#333,stroke-width:1px
    classDef step3 fill:#d5e8d4,stroke:#333,stroke-width:1px
    classDef step4 fill:#dae8fc,stroke:#333,stroke-width:1px
    classDef step5 fill:#ffe6cc,stroke:#333,stroke-width:1px

    class A1,A2,A3 step1
    class B1,B2,B3,B4,B5 step2
    class C1,C2,C3 step3
    class D1,D2 step4
    class E1,E2,E3,E4,E5,E6,E7 step5
```

## SQL Execution Flow Explained

The Points Cost Forecast SQL process follows a structured flow designed to transform raw data into actionable insights:

### Step 1: Create Common Dimension Tables
- **dim_date**: Builds the calendar framework including fiscal periods
- **dim_business_category**: Establishes the business hierarchy mapping
- **dim_day_of_week_weights**: Creates distribution weights for daily allocations

### Step 2: Extract Finance Data
- **finance_actuals**: Extracts actual financial data from the finance system
- **finance_forecast**: Extracts financial forecasts for future periods
- **finance_mapped**: Maps finance data to business/category dimensions
- **article_sales_actuals**: Processes granular article-level sales
- **helper_dimension_combinations**: Creates complete time/business matrix

### Step 3: Process Campaign Costs
- **campaign_details**: Extracts campaign metadata and forecasts
- **campaign_costs_forecast**: Calculates campaign forecasts by business/category
- **campaign_costs_actuals**: Distributes campaign costs to daily granularity

### Step 4: Extract EDX Data
- **everyday_extra_costs**: Processes actual Everyday Extra costs
- **everyday_extra_forecast**: Generates forecasts for EDX program

### Step 5: Create Dashboard Tables
- **dashboard_data**: Combines all metrics into a unified dataset
- **dashboard_summary_***: Creates aggregated views at various levels
- **dashboard_view**: Exposes the data for dashboard consumption

The arrows in the diagram show key dependencies between tables, highlighting which tables must be created before others.
