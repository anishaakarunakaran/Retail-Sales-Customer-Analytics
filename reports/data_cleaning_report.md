# Data Cleaning Report



## Cleaning decisions (with rationale)

| # | Issue | Action | Rationale |
|---|-------|--------|-----------|
| 1 | Invalid order dates (month 00/13) | Rows dropped | Impossible dates cannot be repaired reliably; 0.13% of data |
| 2 | Negative quantity | Rows dropped | Invalid transaction lines |
| 3 | Unit price typos (10x, negative) | Recalculated | Unit_Price = Sales / (Qty * (1-Discount)) |
| 4 | Missing discount ('-') | Derived from Sales/Unit_Price | Discount = 1 - Sales/(Qty*Unit_Price) |
| 5 | Exact duplicate rows | Dropped | Duplicates bias counts |
| 6 | Category casing (e.g. 'technology') | Standardised to Title Case | Inconsistent values break GROUP BY |
| 7 | Missing Age | Imputed with segment median | Age differs by segment (Corporate older, Consumer younger) |
| 8 | Missing City | Imputed with state mode | City belongs to a known state |
| 9 | Non-Completed orders | Excluded from analysis set | Cancelled/Returned/Pending produce no revenue |

## Baseline (Phase 1)
- Rows x columns: [117049, 23]
- Duplicates: 367
- Invalid dates: 140
- Negative quantities: 114
- Negative unit prices: 59
- Missing values: {
  "Age": 1.57,
  "City": 0.95
}

## Cleaning actions (Phase 2)
{
  "invalid_dates_dropped": 209,
  "negative_quantity_dropped": 114,
  "unit_price_recalculated": 208,
  "discount_derived": 1445,
  "unreconcilable_lines_dropped": 0,
  "duplicates_dropped": 370,
  "age_imputed": 1824,
  "city_imputed": 1106,
  "non_completed_excluded": 8309,
  "rows_remaining": 108045
}

## After cleaning
- Cleaned rows: 108,045 (Completed orders only)
- Total sales: $ 68,905,247
- Total profit: $ 16,396,834
- Total orders: 33,209
- Total customers: 1,648
