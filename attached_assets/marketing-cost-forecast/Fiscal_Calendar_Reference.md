# Fiscal Calendar Reference

## Overview
The Points Cost Forecast system uses the Big W fiscal calendar for all reporting. This reference explains how fiscal years, periods, and weeks are structured and mapped to calendar dates.

---

## 1. Fiscal Year Structure

- **Fiscal Year (FY)**: Runs from late June one year to late June the next (e.g., FY25 = 24 June 2024 to 29 June 2025).
- **Fiscal Periods**: Each year is divided into 13 periods (months), each with 4 or 5 weeks.
- **Fiscal Weeks**: Numbered sequentially from 1 to 52 (or 53 in some years).

---

## 2. Mapping Example

| Calendar Date | Fiscal Year | Fiscal Period | Fiscal Week |
|--------------|-------------|--------------|-------------|
| 2024-06-24   | 2025        | 1            | 1           |
| 2024-07-01   | 2025        | 1            | 2           |
| 2024-12-30   | 2025        | 7            | 27          |
| 2025-06-23   | 2025        | 13           | 52          |

---

## 3. How to Look Up Fiscal Dates

- Use the `dim_date` table in the SQL script for mapping calendar to fiscal dates.
- For a complete mapping, see the `FiscalWeekStartDate`, `FiscalYear`, `Fiscal_Period`, and `FiscalWeek` fields.

---

## 4. References
- For detailed fiscal calendars, see the screenshots in `BIGW FY25 Points Cost Forecast (WEEKLY VIEW).pdf` and `BIGW FY25 Points Cost Forecast v2.pdf`.
- For technical mapping logic, see the Technical Documentation.
