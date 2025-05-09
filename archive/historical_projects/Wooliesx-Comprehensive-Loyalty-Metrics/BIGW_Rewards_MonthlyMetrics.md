# BIGW Rewards Monthly KPI Dashboard - SQL Analysis

## Overview

This document analyzes the SQL code for BIGW's Everyday Rewards monthly KPI reporting system. The code creates a comprehensive monitoring framework tracking loyalty program performance, customer behavior, and business impact.

## Data Pipeline Architecture

```mermaid
flowchart TB
    linkStyle default stroke-width:1px;
    
    subgraph "Data Sources"
        A1["Transaction Data"]
        A2["Customer Data"]
        A3["Campaign Data"]
        A4["Subscription Data"]
        A5["Fiscal Calendar"]
    end
    
    subgraph "Helper Tables"
        B1["Time Period Groups"]
        B2["Member Type Classification"]
    end
    
    subgraph "Transaction Processing"
        C1["Basket Analysis"]
        C2["Frequency Analysis"]
        C3["Scan Rates"]
    end
    
    subgraph "Membership Metrics"
        D1["Everyday Extra Subscribers"]
        D2["Booster Members"]
        D3["Redeemer Analysis"]
        D4["Acquisition from Group"]
    end
    
    subgraph "Campaign Analysis"
        E1["AMO Products"]
        E2["EDR Callouts"]
    end
    
    subgraph "Output Tables"
        F1["Performance Trends"]
        F2["KPI Metrics"]
    end
    
    A1 & A2 & A3 & A4 & A5 --> B1 & B2
    B1 & B2 --> C1 & C2 & C3
    C1 & C2 & C3 --> D1 & D2 & D3 & D4
    D1 & D2 & D3 & D4 --> E1 & E2
    E1 & E2 --> F1 & F2
```

## Database Schema Structure

```mermaid
erDiagram
    bigw_time_period_group_monthly ||--o{ temp_bigw_baskets_ORDERID : "time periods"
    temp_bigw_member_type ||--o{ temp_bigw_baskets_ORDERID : "member classification"
    temp_bigw_baskets_ORDERID ||--|{ temp_bigw_freq_data : "frequency"
    temp_bigw_baskets_ORDERID }|--|| temp_bigw_scan_rates : "scan metrics"
    temp_bigw_baskets_ORDERID }|--|| temp_bigw_edX : "subscription data"
    temp_bigw_AMO_PRODUCTS }|--|| temp_bigw_EDR_Callouts : "campaign metrics"
    temp_bigw_scan_rates }|--|| bigw_monthly_performance_trends : "contributes to"
    temp_bigw_edX }|--|| bigw_monthly_performance_trends : "contributes to"
    temp_bigw_EDR_Callouts }|--|| bigw_monthly_performance_trends : "contributes to"
    temp_bigw_add_metrics }|--|| bigw_monthly_performance_trends : "contributes to"
    bigw_monthly_performance_trends }|--|| bigw_monthly_performance_metrics : "formatted for"
```

## ETL Processing Flow

```mermaid
flowchart TD
    linkStyle default stroke-width:1px;
    
    A["Start"] --> B["Create Time Period Groups"]
    B --> C["Identify Member Types"]
    C --> D["Process Baskets & Transactions"]
    D --> E["Calculate Frequency Metrics"]
    D --> F["Analyze Scan Rates"]
    D --> G["Process Everyday Extra Data"]
    
    F --> H["Calculate Customer Annual Value"]
    G --> I["Calculate EDX Subscription Metrics"]
    
    E & H & I --> J["Process Everyday Rewards Metrics"]
    J --> K["Identify AMO Products"]
    K --> L["Calculate EDR Callout Metrics"]
    
    D --> M["Calculate Acquisition from Group"]
    
    L & M --> N["Generate Performance Trends"]
    N --> O["Create Final KPI Dashboard"]
```

## Metrics Calculation Framework

```mermaid
flowchart LR
    linkStyle default stroke-width:1px;
    
    subgraph "Raw Metrics"
        R1["Transaction Data"]
        R2["Member Status"]
        R3["Campaign Data"]
    end
    
    subgraph "Calculated Metrics"
        C1["AOV Calculations"]
        C2["Frequency Metrics"]
        C3["Redemption Metrics"]
        C4["Subscription Metrics"]
    end
    
    subgraph "Business KPIs"
        K1["Value per Member"]
        K2["Acquisition Metrics"]
        K3["Annual Member Spend"]
        K4["Scan Rate Performance"]
    end
    
    R1 --> C1 & C2
    R2 --> C2 & C3
    R3 --> C3 & C4
    
    C1 & C2 & C3 & C4 --> K1 & K2 & K3 & K4
```

## SQL Structure Analysis

The SQL script follows a logical progression:

1. **Helper Tables** - Creates fundamental reference tables:
   - `bigw_time_period_group_monthly`: Maps calendar dates to BIGW's fiscal periods
   - `temp_bigw_member_type`: Customer classification (Staff, EDR Subscriber, EDR Booster, EDR Member)

2. **Transaction Processing** - Processes basket-level data:
   - `temp_bigw_baskets_ORDERID`: Core transaction data for analysis
   - `temp_bigw_freq_data`: Frequency metrics for customer shopping patterns
   - `temp_bigw_scan_rates`: Loyalty card scan rates at different locations

3. **Subscription Analysis** - Analyzes Everyday Extra program:
   - `temp_bigw_edX`: Subscription metrics including sign-ups, AOV, and frequency

4. **Loyalty Program Analysis**:
   - `temp_bigw_AMO_PRODUCTS`: Analysis of Always-on Marketing Offers
   - `temp_bigw_EDR_Callouts`: Everyday Rewards program metrics
   - `temp_bigw_add_metrics`: Additional metrics including acquisition from group

5. **Final Outputs**:
   - `bigw_monthly_performance_trends`: Time series of all metrics
   - `bigw_monthly_performance_metrics`: Formatted dashboard metrics with MoM and YoY comparisons

## Key Business Metrics

1. **OKR Metrics:**
   - Value per member
   - Acquisition from Group
   - Annual Member Spend
   - Scan rate (Overall)
   - Active members (26 weeks)

2. **Everyday Rewards Metrics:**
   - Active member shopping behavior
   - Booster member metrics
   - AMO campaign performance
   - Redeemer analysis

3. **Everyday Extra (Subscription) Metrics:**
   - Subscriber counts
   - New sign-ups
   - Subscriber transaction value
   - Subscription frequency

4. **Additional Insights:**
   - Customer acquisition patterns
   - Category performance
   - Member pricing effectiveness
   - Loyalty program ROI 



   ---



