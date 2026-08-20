# Power BI — DAX Measures (reference)

Copy/paste into a `Measures` table in Power BI Desktop.

```dax
-- =============================================================
-- Core KPIs
-- =============================================================
Total Revenue    = SUM('Orders'[Sales])
Total Profit     = SUM('Orders'[Profit])
Total Cost       = SUM('Orders'[Cost])
Total Quantity   = SUM('Orders'[Quantity])
Total Orders     = DISTINCTCOUNT('Orders'[Order_ID])
Total Customers  = DISTINCTCOUNT('Orders'[Customer_ID])

Avg Order Value  = DIVIDE([Total Revenue], [Total Orders])
Avg Quantity / Order = DIVIDE([Total Quantity], [Total Orders])
Profit Margin    = DIVIDE([Total Profit], [Total Revenue])

-- =============================================================
-- Time intelligence
-- =============================================================
Revenue YoY % =
    VAR Cur = [Total Revenue]
    VAR Prev = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Date'[Date]))
    RETURN DIVIDE(Cur - Prev, Prev)

Revenue MoM % =
    VAR Cur = [Total Revenue]
    VAR Prev = CALCULATE([Total Revenue], PREVIOUSMONTH('Date'[Date]))
    RETURN DIVIDE(Cur - Prev, Prev)

Profit Margin YoY =
    VAR Cur = [Profit Margin]
    VAR Prev = CALCULATE([Profit Margin], SAMEPERIODLASTYEAR('Date'[Date]))
    RETURN Cur - Prev

-- 3-month trailing average revenue (smooths seasonality)
Revenue 3M MA =
    CALCULATE(AVERAGEX(VALUES('Date'[YearMonth]), [Total Revenue]),
              DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -3, MONTH))

-- =============================================================
-- Customer analytics
-- =============================================================
Returning Customers =
    COUNTROWS(FILTER(VALUES('Orders'[Customer_ID]), [Total Orders] > 1))

One-time Customers = [Total Customers] - [Returning Customers]

Avg Customer Value = DIVIDE([Total Revenue], [Total Customers])

Revenue per RFM Segment   = SUM('CustomerRFM'[monetary])
Customers per RFM Segment = COUNTROWS('CustomerRFM')
Segment Revenue Share = DIVIDE([Revenue per RFM Segment],
                               CALCULATE(SUM('CustomerRFM'[monetary]), ALL('CustomerRFM'[Segment])))

-- =============================================================
-- Product & profitability
-- =============================================================
Avg Discount % = AVERAGE('Orders'[Discount])

Margin by Band =
    AVERAGEX(SUMMARIZE('Orders', 'Orders'[Discount_Band], "m",
             DIVIDE(SUM('Orders'[Profit]), SUM('Orders'[Sales]))), [m])

Product Quadrant =
    SWITCH(TRUE(),
        [Total Revenue] >= 1000000 && [Profit Margin] >= 0.25, "High Sales / High Profit",
        [Total Revenue] >= 1000000 && [Profit Margin] <  0.25, "High Sales / Low Profit",
        [Total Revenue] <  1000000 && [Profit Margin] >= 0.25, "Low Sales / High Margin",
        "Low Sales / Low Profit")

Low-Margin High-Volume Flag =
    IF([Total Revenue] > 1000000 && [Profit Margin] < 0.15, 1, 0)
```

### Date table (calculated table)

```dax
Date =
VAR MinDate = MIN('Orders'[Order_Date])
VAR MaxDate = MAX('Orders'[Order_Date])
VAR Cal = CALENDAR(MinDate, MaxDate)
RETURN
ADDCOLUMNS(
    Cal,
    "Year", YEAR([Date]),
    "MonthNo", MONTH([Date]),
    "MonthName", FORMAT([Date], "MMMM"),
    "YearMonth", FORMAT([Date], "YYYY-MM"),
    "Quarter", "Q" & QUARTER([Date]),
    "DayOfWeek", FORMAT([Date], "dddd")
)