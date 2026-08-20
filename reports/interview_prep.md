# Interview Preparation — Retail Sales & Customer Analytics

## 2-Minute Project Explanation (say this out loud)

> "I built an end-to-end analytics project for a multi-region retail business using
> four years of transaction data — about 108,000 order lines, 33,000 orders and
> 1,600 customers.
>
> I started by auditing and cleaning the raw data in Python: fixing missing
> values, duplicates, invalid dates and price typos, and engineering features
> like age groups, discount bands and date parts. Then I did a full exploratory
> analysis and answered 12 business questions in SQL against a normalised
> database I designed — revenue, top products, MoM growth, rankings and Pareto
> analysis.
>
> The most interesting part was the statistics. Management believed discounts
> drive sales, so I tested it: a Welch t-test showed discounted lines have a
> significantly lower margin, and the correlation between discount and quantity
> sold was basically zero — meaning discounts didn't lift volume at all. Lines
> with 30%+ discounts were actually loss-making.
>
> I then segmented all customers using RFM — Recency, Frequency and Monetary —
> and found that the top 33% of customers generate 80% of revenue, and that 123
> at-risk customers hold $4 million of revenue that we could recover.
>
> Everything came together in a four-page Power BI dashboard for executives —
> KPIs, trends, customer segments and product profitability — plus a management
> report with eight prioritised recommendations, like capping discounts,
> running a Champion retention programme and expanding the under-penetrated
> Central region.
>
> The core takeaway: the data showed the fastest growth lever wasn't more
> discounting — it was protecting and recovering the customers we already have."

---

## Python — 10 questions

**1. What is the difference between `loc`, `iloc` and `[]` in pandas?**
`loc` selects by label, `iloc` by integer position, `[]` does column selection
(or boolean masking on a DataFrame). `df.loc[df['Sales']>100, ['Customer_ID']]`
filters rows by condition and columns by label.

**2. How do you handle missing values? Give three options.**
Drop rows (if few and non-representative), impute (mean/median for skewed data,
mode for categorical, or group-based medians), or flag with a new column and
keep the record. In this project I imputed Age with the segment median because
age differs by segment, and City with the state mode.

**3. Why would you use `groupby().agg()` instead of a loop?**
It's vectorised, faster and less error-prone. Example:
`df.groupby('Category').agg(sales=('Sales','sum'), orders=('Order_ID','nunique'))`.

**4. How do you detect and handle outliers?**
Inspect with `describe()`, boxplots and IQR (values beyond Q1−1.5×IQR or
Q3+1.5×IQR). In my data, Unit_Price had 10× typos and negatives; I validated
them against the price identity `Sales = Qty × Price × (1−Discount)` and
recalculated instead of blindly removing.

**5. What is the difference between `apply`, `map` and `transform`?**
`map` transforms one Series with a mapping; `apply` runs a function over a
DataFrame/Series (row/column); `transform` returns the same shape as the input
and is used with `groupby` for aggregation-consistent imputation.

**6. How do you merge two DataFrames?**
`pd.merge(left, right, on=key, how='inner'/'left'/'right'/'outer')`. I joined
customer attributes to the order lines on `Customer_ID`, and RFM scores to the
fact table for Power BI.

**7. Explain the difference between a Series and a DataFrame.**
A Series is a single labelled 1-D array; a DataFrame is a 2-D table of multiple
Series sharing an index.

**8. How would you create the Discount_Band feature?**
`pd.cut` on the Discount column with fixed bins and labels. I used
`pd.cut(df['Discount'], bins=[-0.001,0.001,0.10,0.20,0.30,1.0], labels=[...])`
and learned that a label literally named "None" gets read back as NaN by
`pd.read_csv` — a nice data-quality trap to discuss.

**9. What does `pivot_table` do and when is it useful?**
It reshapes long data into a wide summary table
(`pd.pivot_table(df, index='Region', columns='Category', values='Sales', aggfunc='sum')`),
useful for comparison matrices and reports.

**10. How do you ensure a notebook is reproducible?**
Fixed seed for the RNG, pinned package versions in `requirements.txt`, clear
naming, and loading from the cleaned data file rather than re-cleaning in each
notebook.

---

## SQL — 10 questions

**1. What is the order of execution of a SQL query?**
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT. This is why you
can filter with WHERE but must filter aggregated values with HAVING.

**2. Difference between `WHERE` and `HAVING`?**
WHERE filters rows before aggregation; HAVING filters groups after GROUP BY.
`HAVING COUNT(DISTINCT order_id) > 5` picks customers with more than five orders.

**3. What is a JOIN? Name the types.**
A JOIN combines rows from tables on a key. INNER (only matches), LEFT/RIGHT
(all from one side), FULL OUTER (all from both), CROSS (Cartesian). I joined
`order_items` → `orders` → `customers` to attribute line revenue to customers.

**4. What is a window function and how is it different from GROUP BY?**
A window function computes over a set of rows while keeping every row visible,
e.g. `RANK() OVER (PARTITION BY category ORDER BY revenue DESC)` or a running
total with `SUM(...) OVER (ORDER BY month)`. GROUP BY collapses rows.

**5. What is a CTE and when do you use one?**
`WITH name AS (SELECT ...)` creates a named temporary result set. It makes
multi-step queries readable and reusable, e.g. first computing monthly revenue,
then the MoM growth with `LAG()`.

**6. How would you compute month-over-month growth in SQL?**
`WITH monthly AS (SELECT strftime('%Y-%m', order_date) month, SUM(sales) revenue
FROM orders GROUP BY month) SELECT month, revenue,
(revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month)
AS growth FROM monthly;`

**7. What are `ROW_NUMBER`, `RANK` and `DENSE_RANK` differences?**
ROW_NUMBER gives unique sequential numbers; RANK allows ties with gaps (1,1,3);
DENSE_RANK allows ties without gaps (1,1,2).

**8. How would you find the top 2 customers per region?**
Use a window function: `ROW_NUMBER() OVER (PARTITION BY region ORDER BY spend
DESC) rn` inside a subquery, then `WHERE rn <= 2`.

**9. What is the difference between a subquery and a JOIN?**
A subquery returns a value or set used within another query; a JOIN combines
tables side-by-side. Sometimes interchangeable, but window functions and
correlated subqueries solve things JOINs can't easily express.

**10. What is a primary key vs a foreign key?**
A primary key uniquely identifies a row in its table; a foreign key references
a primary key in another table to enforce referential integrity (e.g.
`orders.customer_id → customers.customer_id`).

---

## Statistics — 10 questions

**1. Difference between mean and median — when does it matter?**
The median resists outliers. When customer spend is right-skewed, median is the
better "typical customer"; mean is pulled up by heavy hitters.

**2. What is standard deviation vs variance?**
Variance is the average squared deviation from the mean; standard deviation is
its square root and is in the same units as the data — more interpretable.

**3. What is the IQR and how is it used?**
IQR = Q3 − Q1, the middle 50% of data. Used for boxplots and outlier bounds
(1.5×IQR rule) and robust variability comparisons.

**4. What is correlation and its limits?**
Pearson r measures the strength and direction of a linear relationship between
−1 and 1. It measures association, not causation — and can miss non-linear
patterns.

**5. How do you interpret a p-value?**
The probability of observing a test statistic at least as extreme as ours, IF
the null hypothesis is true. p < 0.05 → reject H0 (significant). p does NOT
mean the effect is large — check effect size too.

**6. What is a null hypothesis? Give an example from this project.**
H0 is the default claim you test. Example: "The mean profit margin of
discounted lines equals that of non-discounted lines." The Welch t-test gave
p < 0.001, so we rejected H0: discounts do reduce margin.

**7. When do you use a t-test vs ANOVA?**
A t-test compares two group means; ANOVA compares three or more. I used a Welch
t-test for discount vs no-discount margin, and one-way ANOVA for margin across
the four product categories.

**8. What is the difference between a paired and unpaired t-test?**
Paired compares the same subjects before/after; unpaired compares two
independent groups. My discount comparison is unpaired (independent lines).

**9. Why is a large sample "too significant"?**
With N > 100K, even tiny differences become statistically significant. That's
why I report effect sizes (r, mean differences) as the decision-relevant
quantity, not just p-values.

**10. What is Type I vs Type II error?**
Type I: rejecting a true H0 (false positive, risk = α). Type II: failing to
reject a false H0 (false negative, risk = β). α = 0.05 means a 5% chance of
claiming an effect that isn't real.

---

## Power BI — 10 questions

**1. What is the difference between calculated columns and measures?**
Calculated columns are computed row-by-row and stored in the model; measures
are evaluated in context (filtered by the visual). Use measures for aggregates
(revenue, margin) — they respect slicers.

**2. What does DAX CALCULATE do?**
It changes the filter context. Example:
`CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Date'[Date]))` computes revenue
for the previous year regardless of the current slicer selection.

**3. Why use a date table?**
Power BI time intelligence (SAMEPERIODLASTYEAR, PREVIOUSMONTH) requires a
continuous date table related to the fact table. I created one with
`CALENDAR(MIN(...), MAX(...))`.

**4. What is the difference between a relationship and a measure?**
A relationship defines how tables connect (cardinality and direction); a
measure defines a calculation that operates across those relationships.

**5. How do you build a drill-down hierarchy?**
Create a hierarchy (Region → State → City) or stack columns in a matrix/bar
visual's axis, then use the drill-down arrows in the visual header.

**6. What are slicers and how do you sync them across pages?**
Slicers are visual filters. View → Sync slicers propagates a slicer's
selection to other pages, keeping the dashboard coherent.

**7. What is the difference between import and DirectQuery?**
Import copies data into the model (fast, refreshes on schedule); DirectQuery
queries the source live (large data, real-time, but slower). For a portfolio
dataset, import mode is right.

**8. How would you show revenue by RFM segment?**
Relate the fact table to the CustomerRFM dimension on Customer_ID, put
Segment on the axis and `SUM('CustomerRFM'[monetary])` as the value — or a
measure that sums sales filtered by segment.

**9. What is a KPI card?**
A single-value visual for a measure (e.g., Total Revenue). You can add
trends and target comparisons with conditional formatting.

**10. How do you handle duplicate values or inconsistent naming between
tables in Power Query?**
In Power Query Editor: remove duplicates, merge/replace values for casing,
change types and rename tables — exactly the cleaning done in Python here.

---

## Business Analytics — 10 questions

**1. What is the difference between descriptive, diagnostic, predictive and
prescriptive analytics?**
Descriptive: what happened (revenue trend). Diagnostic: why (discounts hurt
margin). Predictive: what will happen (demand forecast). Prescriptive: what to
do (cap discounts, run retention campaigns). This project covers all four.

**2. How do you define a "high-value" customer?**
By revenue contribution (top quartile) or lifetime value. In this dataset the
top 25% of customers by spend drive 74% of revenue — a classic Pareto pattern.

**3. What is RFM and why is it useful?**
Recency (how recently they bought), Frequency (how often), Monetary (how much).
It groups customers into actionable segments without machine learning.

**4. How would you decide whether a discount campaign worked?**
Compare margin and quantity with vs without discount using a controlled test
or statistical test, controlling for seasonality. Here, the correlation of
discount with quantity was ~0 and margin collapsed — evidence against blanket
discounts.

**5. What KPIs would you show an executive?**
Revenue, profit, margin, orders, customers, AOV, growth % — the six KPI cards
on the Executive Overview page.

**6. How do you turn a finding into a recommendation?**
Use the structure Finding → Evidence → Impact → Recommendation. Example:
Finding (30%+ discounts lose money), Evidence (−8.2% margin, $305K loss),
Impact (profit leakage), Recommendation (cap discounts at 15%).

**7. What is customer churn and how do you measure it?**
Churn is customers who stop buying. Measured via recency — e.g., Lost segment
(no purchase in 63+ weeks on average here) and At-Risk/Can't-Lose (recently
active, now quiet, worth $4.0M).

**8. Why might a category have high revenue but low profit?**
High volume at thin margins — Technology has 38% of revenue at 12.4% margin
because cost prices and competition squeeze it; the fix is cost negotiation or
cross-sell of high-margin categories.

**9. What is seasonality and how does it affect planning?**
Predictable demand patterns within the year. December is 2.4x July here, so
inventory, staffing and marketing must peak around Nov–Dec and Aug–Sep.

**10. What is an average order value and how do you improve it?**
AOV = revenue / orders ($2,074 here). Improve via cross-sell, bundles,
minimum-order offers and targeting high-AOV segments (Corporate AOV $2,558 vs
Consumer $1,221).

---

## RFM / Customer Analytics — 5 questions

**1. Explain how you computed RFM scores.**
For each customer: Recency = days since last order, Frequency = number of
orders, Monetary = total spend. Then scored each 1–5 by quintile, inverting
recency so fresher = higher. Final score = R×100 + F×10 + M.

**2. What are the RFM segments and how did you name them?**
Champions (high R/F/M), Loyal, Potential Loyalists, New, Promising,
Hibernating, At-Risk, Can't-Lose (big spenders going quiet), Lost. Rules are
in `python/rfm_analysis.py`.

**3. What was your most interesting RFM insight?**
Concentration: Champions + Loyal = 33% of customers = 80% of revenue, while 536
Lost customers still hold $3.0M of spend. Retention is the highest-ROI lever.

**4. How would you act on the "Can't Lose" segment?**
They used to be high-value and stopped buying (here: 43 customers, $2.2M,
~18 weeks inactive). Personalised win-back with a human touch and a limited
offer — no blanket discounts, which we know destroy margin.

**5. What are the limitations of RFM?**
It's static (a snapshot), ignores product mix and cost-to-serve, and does not
predict future value. Improvements: predict CLV, add engagement signals and
refresh monthly.

---

## Bonus: 5 common mistakes to avoid in interviews

1. Quoting metric improvements you didn't measure — always say "computed from
   the dataset".
2. Saying "p-value is the probability H0 is true" — it isn't.
3. Confusing `WHERE` (row filter) and `HAVING` (group filter).
4. Forgetting that correlation ≠ causation (discount vs volume ≈ 0).
5. Treating a t-test result as "big" without looking at the effect size.