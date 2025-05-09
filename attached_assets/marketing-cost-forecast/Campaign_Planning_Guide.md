# Campaign Planning Guide

## Overview
This guide explains how to plan, configure, and analyze marketing campaigns in the Points Cost Forecast system, ensuring accurate cost forecasting and reporting.

---

## 1. Campaign Streams & Types

- **Streams**: Campaigns are grouped by stream (e.g., XBan, ATL, BTL, Trade, Category, Everyday Extra).
- **Types**: Each stream may have subtypes (e.g., BTL for below-the-line, ATL for above-the-line).
- **Reference**: See the `campaignStream` and `CampaignCategoryType` fields in the SQL script and campaign details table.

---

## 2. Campaign Forecasting

- **Input**: Campaign budgets and forecasts are entered in the marketing plan (see `bigw_campaign_details_planOnPage_FY25_static.bqsql`).
- **Forecast Logic**: Budgets are allocated by week and distributed to business/category based on sales proportions.
- **Cost Calculation**: Costs are calculated using basis point rates (e.g., 50bps, 70bps).

---

## 3. Example Campaign Setup

| Campaign Stream | Category   | Start Date  | End Date    | Budget   |
|-----------------|------------|-------------|-------------|----------|
| XBan_BTL        | Storewide  | 2025-06-23  | 2025-06-29  | $150,000 |
| ATL_PoP         | Toys       | 2025-07-01  | 2025-07-07  | $50,000  |

---

## 4. Best Practices

- **Align with Business Mapping**: Ensure campaigns are mapped to valid business/category combinations.
- **Update Forecasts Promptly**: Enter new campaigns or budget changes as soon as they are approved.
- **Review Actuals**: After campaign completion, compare actual costs to forecast for variance analysis.

---

## 5. References
- See the Technical Documentation for campaign allocation logic.
- For campaign detail fields, see `BIGW FY25 Points Cost Forecast (WEEKLY VIEW).pdf` and `BIGW FY25 Points Cost Forecast v2.pdf`.
