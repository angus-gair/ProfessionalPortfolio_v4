# Retail Loyalty Program Analytics Dashboard - Technical Architecture

## Overview

This document outlines the technical architecture for a comprehensive retail loyalty program analytics system. The solution provides detailed insights into customer behavior, program performance, and business impact through an integrated data pipeline and KPI framework.

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
        B1["Fiscal Calendar Mapping"]
        B2["Member Type Classification"]
    end
    
    subgraph "Transaction Processing"
        C1["Basket Analysis"]
        C2["Frequency Analysis"]
        C3["Scan Rates"]
    end
    
    subgraph "Membership Metrics"
        D1["Premium Subscription Members"]
        D2["Engaged Members"]
        D3["Offer Redemption Analysis"]
        D4["Acquisition from Group"]
    end
    
    subgraph "Campaign Analysis"
        E1["Targeted Product Offers"]
        E2["Loyalty Program Metrics"]
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
    time_period_mapping ||--o{ transaction_baskets : "time periods"
    member_classification ||--o{ transaction_baskets : "member classification"
    transaction_baskets ||--|{ frequency_metrics : "frequency"
    transaction_baskets }|--|| scan_metrics : "scan metrics"
    transaction_baskets }|--|| subscription_metrics : "subscription data"
    marketing_offers }|--|| loyalty_metrics : "campaign metrics"
    scan_metrics }|--|| performance_trends : "contributes to"
    subscription_metrics }|--|| performance_trends : "contributes to"
    loyalty_metrics }|--|| performance_trends : "contributes to"
    additional_metrics }|--|| performance_trends : "contributes to"
    performance_trends }|--|| performance_dashboard : "formatted for"
```

## ETL Processing Flow

```mermaid
flowchart TD
    linkStyle default stroke-width:1px;
    
    A["Start"] --> B["Create Fiscal Period Mapping"]
    B --> C["Identify Member Types"]
    C --> D["Process Baskets & Transactions"]
    D --> E["Calculate Frequency Metrics"]
    D --> F["Analyze Scan Rates"]
    D --> G["Process Premium Subscription Data"]
    
    F --> H["Calculate Customer Annual Value"]
    G --> I["Calculate Subscription Metrics"]
    
    E & H & I --> J["Process Loyalty Program Metrics"]
    J --> K["Identify Targeted Product Offers"]
    K --> L["Calculate Loyalty Program Metrics"]
    
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

The SQL implementation follows a logical progression:

1. **Helper Tables** - Creates fundamental reference tables:
   - `time_period_mapping`: Maps calendar dates to fiscal periods
   - `member_classification`: Customer classification system (Premium, Engaged, Standard, etc.)

2. **Transaction Processing** - Processes basket-level data:
   - `transaction_baskets`: Core transaction data for analysis
   - `frequency_metrics`: Frequency metrics for customer shopping patterns
   - `scan_metrics`: Loyalty card scan rates at different locations

3. **Subscription Analysis** - Analyzes premium subscription program:
   - `subscription_metrics`: Subscription metrics including sign-ups, AOV, and frequency

4. **Loyalty Program Analysis**:
   - `marketing_offers`: Analysis of targeted product offers
   - `loyalty_metrics`: Loyalty program performance metrics
   - `additional_metrics`: Additional metrics including acquisition from group

5. **Final Outputs**:
   - `performance_trends`: Time series of all metrics
   - `performance_dashboard`: Formatted dashboard metrics with MoM and YoY comparisons

## Key Business Metrics

1. **OKR Metrics:**
   - Value per member
   - Acquisition from Group
   - Annual Member Spend
   - Scan rate (Overall)
   - Active members (26 weeks)

2. **Loyalty Program Metrics:**
   - Active member shopping behavior
   - Engaged member metrics
   - Marketing offer performance
   - Offer redemption analysis

3. **Premium Subscription Metrics:**
   - Subscriber counts
   - New sign-ups
   - Subscriber transaction value
   - Subscription frequency

4. **Additional Insights:**
   - Customer acquisition patterns
   - Category performance
   - Member offers effectiveness
   - Loyalty program ROI 



 ### Comprehensive Data Pipeline for BIGW

**Client:** BIGW Marketing Team  
**Focus:** ETL, Data Integration, Marketing Analytics, Business Intelligence

Developed a comprehensive data pipeline and analytics solution to integrate marketing campaign data, customer behavior, and sales performance across multiple business units, enabling data-driven decision making for marketing strategy.

**Project Highlights:**

- **Designed and implemented a sophisticated ETL pipeline integrating multiple data sources:**
    - Customer transaction data across 5 business destinations
    - Marketing campaign performance metrics (ATL/BTL)
    - Subscription program data (Everyday Extra)
    - Geographic market segmentation
    - Customer loyalty metrics
- **Created a unified data model that:**
    - Maps customer behavior across different geographic markets
    - Tracks campaign effectiveness by business unit
    - Monitors subscription program performance
    - Measures loyalty program engagement
- **Built a scalable analytics framework that:**
    - Processes over 170M customer transactions
    - Handles complex geographic segmentation (Metro/Regional markets)
    - Supports multiple business units (Clothing, Home Living, Toys & Leisure, etc.)
    - Enables granular analysis at store/postcode level
- **Delivered actionable insights:**
    - Identified key performance drivers by business unit
    - Tracked subscription program growth and impact
    - Measured campaign effectiveness across different market segments
    - Enabled data-driven marketing budget allocation

**Tools & Technologies:**  
SQL, Python (pandas, numpy), Tableau, Power BI, AWS