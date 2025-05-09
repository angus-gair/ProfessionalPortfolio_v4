# Points-Cost-Forecast: Technical Project Summary

## Project Objective
This project is designed to compare forecasted budget costs against actual incurred costs, at multiple levels of business granularity:
- **Business Destination/Category**: High-level business units or product families.
- **Individual Item Level**: Down to SKU or campaign stream.
The aim is to provide actionable insights into where budget forecasts align or diverge from real outcomes, supporting both operational and strategic decision-making.

---

## Key Components & Data Flow

### 1. SQL & bqsql Files
- **ETL and Data Modeling**: Files like `2_FInaceTables.sql`, `bigw_cost_model*.bqsql`, and `1_Bigw_points_costs_Forecast_Dashboard_Data*.SQL` define the transformation logic for extracting, joining, and aggregating financial, sales, and campaign data.
- **Finance Table Example**:  
  `2_FInaceTables.sql` constructs a finance metrics table by combining actuals from BigW’s finance system, mapping to business/category hierarchies, and calculating metrics such as gross sales, discounts, loyalty rewards, COGS, and gross profit. It also links these to master data for business/category mapping.
- **Forecasting**:  
  Other SQL files (e.g., `bigw_cost_model_fy25_sales_forecast.bqsql`) model forecasted costs by week, category, and business, often using campaign streams as the lowest granularity.

### 2. JSON Data
- **Actuals and Forecasts**:  
  The file `bigw_cost_model_forecast_fy25.json` contains detailed, structured data for each forecasted campaign or business line, including fields like `costs_forecast_50exclGST`, `costs_budget_fcast`, `cost_20bps_forecast`, and `cost_70bps_forecast`. This enables granular comparison between forecast and actuals, by business, category, week, and campaign.
- **Data Structure Example**:
  ```json
  {
    "Funded_By_Adj": "BIGW",
    "campaignStream": "camp_XBan_BTL_s",
    "Category": "Pet",
    "costs_forecast_50exclGST": 3533.11,
    "costs_budget_fcast": 150000,
    "Business": "Everyday Celebrations & Events",
    ...
  }
  ```

### 3. PDF Dashboard Overviews
- Files such as `BIGW FY25 Points Cost Forecast v2.pdf` and `(WEEKLY VIEW).pdf` provide a visual framing of the dashboard, showing how the data is presented to stakeholders—likely including charts, tables, and summaries comparing forecast vs. actuals.

---

## Technical Workflow

1. **Data Extraction**:  
   Pull actuals and forecasts from various source systems (BigQuery tables, finance systems, campaign management).
2. **Data Transformation**:  
   Use SQL and bqsql scripts to clean, aggregate, and join data at business, category, and item levels.
3. **Data Storage**:  
   Store processed data in intermediate and final tables (e.g., `pf_Actuals_Finance_Metrics`).
4. **Comparison Logic**:  
   Calculate variances between forecast and actuals, both in aggregate and at granular levels.
5. **Visualization**:  
   Output is designed for dashboards, with PDFs providing the framing and JSON/CSV enabling dynamic, data-driven visualizations.

---

## Mermaid Data Flow Diagram (for HTML/Markdown)

````mermaid
flowchart TD
    A[Raw Data Sources\n(Finance, Sales, Campaigns)] --> B[SQL/bqsql ETL Scripts\n(e.g., 2_FInaceTables.sql)]
    B --> C[Aggregated Finance & Forecast Tables]
    C --> D[JSON/CSV Export\n(bigw_cost_model_forecast_fy25.json)]
    C --> E[PDF Dashboards]
    D --> F[Dashboard/BI Tool]
    E --> F
    F[Stakeholder Insights\nForecast vs Actuals]
````

---

## Cleaned/Tidy Version Recommendation

- **Create a subfolder**: `Points-Cost-Forecast/cleaned`
- **Copy only unique, relevant files**:
  - `2_FInaceTables.sql` (core finance logic)
  - `bigw_cost_model_forecast_fy25.json` (actuals & forecasts)
  - Key ETL scripts (remove duplicates/old versions)
  - One or two representative PDFs for dashboard framing
  - Any summary markdown/HTML files
- **Remove**: test files, redundant/old scripts, and duplicates.

---

## Summary

This project is a robust, multi-level financial analytics solution for comparing forecasted and actual costs across the BigW business. It leverages SQL/bqsql for ETL and modeling, JSON for granular data, and PDFs for visualization framing. The output supports business decisions by highlighting variances and trends, all the way down to the item or campaign stream level.

**Next steps:**
- Let me know if you want the cleaned folder created and which files to prioritize.
- I can generate the HTML/mermaid file for you if desired.
- If you want a more detailed file-by-file technical breakdown or code/data extraction, just specify!
