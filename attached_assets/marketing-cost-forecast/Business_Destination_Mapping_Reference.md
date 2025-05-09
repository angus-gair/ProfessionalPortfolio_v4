# Business Destination Mapping Reference

## Overview
Business destination mapping is critical for accurate cost allocation and reporting in the Points Cost Forecast system. This document explains the mapping logic, source tables, and maintenance process.

---

## 1. Mapping Structure

- **Business**: Top-level business unit (e.g., Everyday Celebrations & Events)
- **Category**: Subdivision within a business (e.g., Pet, Toys, Apparel)
- **SubCategory**: More granular grouping, used for mapping to article master data.

---

## 2. Source Table

- **Table**: `gcp-wow-rwds-ai-data-prod.outbound.BigW_Destination_Business`
- **Fields**: `Business`, `Category`, `SubCategory`
- **Reference in SQL**: See the `dim_business_category` table in the production SQL script.

---

## 3. Example Mapping Table

| Business                      | Category       | SubCategory     |
|-------------------------------|---------------|-----------------|
| Everyday Celebrations & Events| Pet           | Pet Food        |
| Home & Living                 | Furniture     | Bedroom         |
| General                       | General       | General         |

---

## 4. Maintenance

- **Updating Mappings**: To add or update a mapping, edit the source table and re-run the ETL pipeline.
- **Best Practices**:
  - Ensure all categories and subcategories are mapped to a business.
  - Avoid NULLs except for intentionally unmapped records.
- **Troubleshooting**: If a business/category is missing from reports, check for mapping errors or missing subcategories.

---

## 5. References
- See the Technical Documentation for more on mapping logic.
- For advanced mapping, see the article master join logic in the SQL script.
