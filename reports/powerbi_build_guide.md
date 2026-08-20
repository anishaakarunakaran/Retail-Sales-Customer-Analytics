# Power BI Dashboard — Build Guide

This project's cleaned data is ready for Power BI. This guide takes you from
the two input files to the finished 4-page dashboard in about 30 minutes.
All numbers in your dashboard will match the Python/SQL analysis because the
source is the same cleaned dataset.

## 1. Input files (already prepared)

| File | Role |
|------|------|
| `data/cleaned/retail_sales_clean.csv` | Fact table (order-line level, Completed orders only, 108,045 rows) |
| `data/cleaned/customer_rfm.csv` | Customer dimension with RFM scores + segment (1,648 customers) |
| `data/retail.db` (optional) | SQLite star schema if you want to import via the SQLite connector |

## 2. Import into Power BI Desktop

1. **Get data → Text/CSV** → select `retail_sales_clean.csv` → Transform Data.
2. In Power Query Editor:
   - Set `Order_Date` type to **Date**.
   - Rename table to `Orders`.
   - Close & Apply.
3. **Get data → Text/CSV** → `customer_rfm.csv` → rename table `CustomerRFM` → Close & Apply.
4. **Model view** → create relationship:
   - `Orders[Customer_ID]` (many) → `CustomerRFM[Customer_ID]` (one).

> Optional star schema: instead of the flat file, connect to the SQLite DB
> (`data/retail.db`) via ODBC and import `orders`, `order_items`, `customers`,
> `products`, `payments`, `locations`, then build relationships.

## 3. Create a Date table (for clean time intelligence)

```dax
Date = CALENDAR(MIN('Orders'[Order_Date]), MAX('Orders'[Order_Date]))
```

Add calculated columns: `Year`, `MonthNo`, `MonthName`, `YearMonth`
(`FORMAT([Date], "YYYY-MM")`). Relate `Date[Date]` (one) → `Orders[Order_Date]`
(many). In the report use **Date columns** for all time visuals.

## 4. DAX measures — create a `Measures` table

```dax
Total Revenue    = SUM('Orders'[Sales])
Total Profit     = SUM('Orders'[Profit])
Total Cost       = SUM('Orders'[Cost])
Total Orders     = DISTINCTCOUNT('Orders'[Order_ID])
Total Customers  = DISTINCTCOUNT('Orders'[Customer_ID])
Total Quantity   = SUM('Orders'[Quantity])

Avg Order Value  = DIVIDE([Total Revenue], [Total Orders])
Profit Margin    = DIVIDE([Total Profit], [Total Revenue])

Revenue YoY %    = 
    VAR CurrentY = [Total Revenue]
    VAR PrevY = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Date'[Date]))
    RETURN DIVIDE(CurrentY - PrevY, PrevY)

Revenue MoM %    = 
    VAR CurM = [Total Revenue]
    VAR PrevM = CALCULATE([Total Revenue], PREVIOUSMONTH('Date'[Date]))
    RETURN DIVIDE(CurM - PrevM, PrevM)

Avg Discount %   = AVERAGE('Orders'[Discount])

Avg Margin by Band = 
    AVERAGEX(
        SUMMARIZE('Orders', 'Orders'[Discount_Band], "m",
            DIVIDE(SUM('Orders'[Profit]), SUM('Orders'[Sales]))),
        [m])

New Customers (period) =
    VAR FirstYear = CALCULATE(MIN('Orders'[Order_Date]), ALLEXCEPT('Orders', 'Date'[Year]))
    RETURN COUNTROWS(FILTER(VALUES('Orders'[Customer_ID]), FirstYear IN VALUES('Date'[Year])))
```

> The RFM segment metrics come straight from the `CustomerRFM` table:
> segment → `CustomerRFM[Segment]`; customers → `COUNTROWS(CustomerRFM)`;
> segment revenue → `SUM(CustomerRFM[monetary])`.

## 5. Page 1 — Executive Overview

Layout (left → right, top → bottom):

| Position | Visual | Fields |
|----------|--------|--------|
| Top row | 6 KPI cards | Total Revenue, Total Profit, Total Orders, Total Customers, Avg Order Value, Profit Margin |
| Left | Line chart "Monthly Revenue Trend" | Axis: `Date[YearMonth]`, Values: `[Total Revenue]` |
| Middle | Line chart "Monthly Profit Trend" | Axis: `Date[YearMonth]`, Values: `[Total Profit]` |
| Right top | Clustered bar "Sales by Category" | Category, `[Total Revenue]` |
| Right mid | Column "Sales by Region" | Region, `[Total Revenue]` |
| Bottom | Horizontal bar "Top 10 Products by Revenue" | Product_Name (Top N = 10), `[Total Revenue]` |

**Slicers** (top band, all pages): `Date[Year]` (list), `Category` (dropdown),
`Region` (dropdown), `Customer_Segment` (dropdown), `Payment_Method` (dropdown).
Sync them across pages via **View → Sync slicers**.

## 6. Page 2 — Sales Analytics

| Visual | Fields |
|--------|--------|
| KPI cards | Revenue, Profit, Quantity, Orders |
| Line "Revenue trend" | `Date[YearMonth]` × `[Total Revenue]` |
| Line "Profit trend" | `Date[YearMonth]` × `[Total Profit]` |
| Line "Quantity trend" | `Date[YearMonth]` × `[Total Quantity]` |
| Clustered bar "Category performance" | Category × Revenue |
| Matrix/bar "Sub-category performance" | Sub_Category × Revenue |
| Bar "Product ranking" | Product_Name × Revenue |
| Map or stacked bar "Regional sales" | Region/State/City |

**Drill-down Region → State → City:** add a matrix visual with Rows =
`Region`, then `State`, then `City` (three levels). Enable **down** arrow icon
in the visual header. Values: `[Total Revenue]`, `[Total Profit]`.

## 7. Page 3 — Customer Analytics

| Visual | Fields |
|--------|--------|
| KPI cards | Total Customers, New Customers, Returning Customers, Avg Customer Value |
| Donut "Customers per RFM segment" | `CustomerRFM[Segment]`, `COUNTROWS(CustomerRFM)` |
| Stacked bar "Revenue by RFM segment" | `CustomerRFM[Segment]` × `SUM(CustomerRFM[monetary])` |
| Bar "Purchase frequency" | `CustomerRFM[orders]` (binned) × `COUNTROWS(CustomerRFM)` |
| Table "Segment profile" | Segment, customers, avg_spend, avg_orders, avg_recency_weeks |

New vs Returning measures:
```dax
Returning Customers =
    COUNTROWS(FILTER(VALUES('Orders'[Customer_ID]), [Total Orders] > 1))
One-time Customers  = [Total Customers] - [Returning Customers]
```

## 8. Page 4 — Product & Profitability

| Visual | Fields |
|--------|--------|
| Top products by sales | Product_Name (Top N 10) × `[Total Revenue]` |
| Top products by profit | Product_Name (Top N 10) × `[Total Profit]` |
| Low-margin products (high volume) | Product_Name filter margin < 10% × Revenue |
| Scatter "Sales vs Profit" | X: Revenue, Y: Profit, Size: Quantity, Legend: Category |
| Scatter "Discount vs Profit margin" | X: `[Avg Discount %]`, Y: `[Avg Margin by Band]`, Legend: Discount_Band |
| Line "Discount effect" | `Discount_Band` × `[Profit Margin]` |

Quadrant colours can be added with a conditional-format measure:
```dax
Product Quadrant =
    SWITCH(TRUE(),
        [Total Revenue] >= 1000000 && [Profit Margin] >= 0.25, "High Sales / High Profit",
        [Total Revenue] >= 1000000 && [Profit Margin] <  0.25, "High Sales / Low Profit",
        [Total Revenue] <  1000000 && [Profit Margin] >= 0.25, "Low Sales / High Margin",
        "Low Sales / Low Profit")
```

## 9. Cross-check numbers with Python/SQL

After building, verify: Total Revenue = **$68,905,247**, Total Profit =
**$16,396,834**, Orders = **33,209**, Customers = **1,648**, AOV = **$2,074.90**,
Margin = **23.8%**. If these match, your model is correct.