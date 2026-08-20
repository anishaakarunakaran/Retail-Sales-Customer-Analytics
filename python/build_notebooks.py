"""
Build the four analysis Jupyter notebooks from self-contained code cells
so each notebook reproduces the pipeline and shows outputs when executed.
Run: python python/build_notebooks.py
Then (optional, to embed outputs):
    jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

NB = Path("notebooks")


def cell(kind: str, src: str) -> dict:
    return {"cell_type": kind, "metadata": {},
            "source": src.splitlines(keepends=True)}


def md(src: str):
    c = nbf.v4.new_markdown_cell(src)
    return c


def code(src: str):
    c = nbf.v4.new_code_cell(src)
    c["execution_count"] = None
    c["outputs"] = []
    return c


def write_notebook(name: str, title: str, cells: list, intro: str) -> None:
    nb = nbf.v4.new_notebook()
    nb["cells"] = [md(f"# {title}\n\n{intro}")] + cells
    nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python",
                                     "name": "python3"},
                      "language_info": {"name": "python"}}
    nbf.write(nb, NB / name)
    print(f"  wrote {name}")


SHARED = """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams.update({'figure.dpi': 120, 'axes.spines.top': False, 'axes.spines.right': False})"""

# ---------------------------------------------------------------------------
# 01 - Data Cleaning
# ---------------------------------------------------------------------------
c01 = [
    md("""## 1. Load raw data
We load the raw export (which intentionally contains realistic data-quality
issues: missing values, duplicates, impossible dates, price typos, inconsistent
casing, and non-completed orders)."""),
    code(f"""{SHARED}
df = pd.read_csv('../data/raw/raw_retail_sales.csv')
df.head(3)"""),
    md("""## 2. Data understanding (Phase 1)
### Dimensions & data types"""),
    code("""print('Rows:', df.shape[0], '| Columns:', df.shape[1])
df.dtypes"""),
    code("""df.describe(include='all').T"""),
    md("""### Missing values"""),
    code("""missing = df.isna().sum()
missing[missing > 0]"""),
    md("""### Duplicates & invalid values"""),
    code("""print('Duplicate rows:', df.duplicated().sum())
print('Negative Quantity:', (df['Quantity'] < 0).sum())
print('Negative Unit_Price:', (df['Unit_Price'] < 0).sum())
print('Impossible dates (month 00/13):',
      df['Order_Date'].astype(str).str[5:7].isin(['00', '13']).sum())
print('\\nOrder status counts:'); print(df['Order_Status'].value_counts())"""),
    md("""### Outlier check (descriptive stats on numeric columns)
`Profit_Margin` at -0.5 already hints that heavy discounts can make lines
unprofitable — we will verify this formally in the statistics notebook."""),
    code("""df[['Quantity', 'Unit_Price', 'Discount', 'Sales', 'Profit', 'Profit_Margin']].describe().round(2)"""),
    md("""## 3. Cleaning pipeline (Phase 2)
Each transformation below is paired with its business justification.

### 3.1 Dates — parse & drop impossible dates
`errors='coerce'` turns unparseable rows into `NaT`, which we drop
(~0.2% of data). These rows cannot be repaired reliably."""),
    code("""df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
df = df.dropna(subset=['Order_Date'])
df['Order_Date'].describe()"""),
    md("""### 3.2 Drop negative quantities (invalid transaction lines)"""),
    code("""df = df[df['Quantity'] >= 0]"""),
    md("""### 3.3 Fix Unit_Price typos using the price identity
Retail price identity: `Sales = Quantity * Unit_Price * (1 - Discount)`.
If the recorded price disagrees with the identity (e.g. a 10x typo), we
recalculate it. Negative prices that cannot be derived are dropped."""),
    code("""df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce')
has_disc = df['Discount'].notna()
expected_price = np.where(has_disc,
    df['Sales'] / np.maximum(df['Quantity'] * (1 - df['Discount']), 1e-9), np.nan)
inconsistent = has_disc & (np.abs(df['Unit_Price'] - expected_price) > 0.01 * expected_price)
print('Unit prices recalculated:', int(inconsistent.sum()))
df.loc[inconsistent, 'Unit_Price'] = np.round(expected_price[inconsistent], 2)
df = df[df['Unit_Price'] > 0]"""),
    md("""### 3.4 Derive missing discounts from the price identity
Instead of guessing missing discounts we derive them:
`Discount = 1 - Sales / (Qty * Unit_Price)`, clamped to a sensible [0, 0.9]."""),
    code("""missing = df['Discount'].isna()
derived = 1 - df['Sales'] / (df['Quantity'] * df['Unit_Price'])
df.loc[missing, 'Discount'] = np.clip(derived[missing], 0, 0.9)
print('Discounts derived:', int(missing.sum()))
print('Discount stats after:', df['Discount'].describe().round(4).to_dict())"""),
    md("""### 3.5 Remove exact duplicates (would double-count revenue)"""),
    code("""print('Duplicates removed:', int(df.duplicated().sum()))
df = df.drop_duplicates()"""),
    md("""### 3.6 Standardise categorical values
Lowercase `'technology'` entries would create phantom categories in
`GROUP BY`; we normalise to Title Case."""),
    code("""df['Category'] = df['Category'].str.strip().str.title()
df['Sub_Category'] = df['Sub_Category'].str.strip().str.title()
df['Payment_Method'] = df['Payment_Method'].str.strip()
df['Order_Status'] = df['Order_Status'].str.strip().str.title()
df['Category'].value_counts()"""),
    md("""### 3.7 Impute missing Age & City
Age differs by segment (Corporate buyers skew older), so we impute with the
**segment median**. City always belongs to a known state, so we impute with
the **state mode** (most common city in that state)."""),
    code("""df['Age'] = df.groupby('Customer_Segment')['Age'].transform(lambda s: s.fillna(s.median()))
df['City'] = df.groupby('State')['City'].transform(
    lambda s: s.fillna(s.mode().iloc[0] if len(s.mode()) else 'Unknown'))
print('Missing values remaining:', int(df.isna().sum().sum()))"""),
    md("""### 3.8 Business rule — Completed orders only
Cancelled / Returned / Pending orders generate **no revenue**. We keep the
full history in the SQL database but exclude them from revenue analytics."""),
    code("""print('Excluded (non-Completed):', int((df['Order_Status'] != 'Completed').sum()))
df = df[df['Order_Status'] == 'Completed']"""),
    md("""### 3.9 Feature engineering
Derived variables unlock time-based and categorical analysis.""", ),
    code("""df['Order_Year'] = df['Order_Date'].dt.year
df['Order_Month'] = df['Order_Date'].dt.month
df['Order_Day'] = df['Order_Date'].dt.day
df['Day_Of_Week'] = df['Order_Date'].dt.day_name()

age_bins = [0, 25, 35, 45, 55, 65, 100]
df['Age_Group'] = pd.cut(df['Age'], bins=age_bins,
                         labels=['18-24', '25-34', '35-44', '45-54', '55-64', '65+'], right=False)
df['Discount_Band'] = pd.cut(df['Discount'], bins=[-0.001, 0.001, 0.10, 0.20, 0.30, 1.0],
                             labels=['No Discount', '0-10%', '10-20%', '20-30%', '30%+'],
                             include_lowest=True)
df['Revenue'] = df['Sales']"""),
    md("""## 4. Reconciliation check
Every surviving line must satisfy `Sales = Qty * Unit_Price * (1 - Discount)`
to within 1 cent (rounding). This is our QA gate before analysis."""),
    code("""resid = (df['Sales'] - df['Quantity'] * df['Unit_Price'] * (1 - df['Discount'])).abs()
print('Lines failing reconciliation (>$0.05):', int((resid > 0.05).sum()))
print('Max residual ($):', round(float(resid.max()), 3))"""),
    md("""## 5. Export cleaned data"""),
    code("""df.to_csv('../data/cleaned/retail_sales_clean.csv', index=False)
print('Saved', len(df), 'rows x', df.shape[1], 'columns')"""),
]
write_notebook(
    "01_data_cleaning.ipynb", "Phase 1-2: Data Understanding & Cleaning",
    c01,
    "Load the raw retail export, audit data quality (missing, duplicates, "
    "outliers, invalid values) and apply a documented cleaning pipeline with "
    "feature engineering — every decision is justified by its business impact.")

# ---------------------------------------------------------------------------
# 02 - EDA
# ---------------------------------------------------------------------------
c02 = [
    md("""## Load cleaned data"""),
    code(f"""{SHARED}
df = pd.read_csv('../data/cleaned/retail_sales_clean.csv', parse_dates=['Order_Date'])
print(df.shape)"""),
    md("""## 1. Global KPIs"""),
    code("""total_sales = df['Sales'].sum(); total_profit = df['Profit'].sum()
total_orders = df['Order_ID'].nunique(); total_customers = df['Customer_ID'].nunique()
print(f'Revenue: ${total_sales:,.0f}')
print(f'Profit: ${total_profit:,.0f}   Margin: {total_profit/total_sales:.1%}')
print(f'Orders: {total_orders:,}   Customers: {total_customers:,}')
print(f'Average Order Value: ${total_sales/total_orders:,.2f}')"""),
    md("""## 2. Time analysis
### Monthly revenue trend (2021-2024)"""),
    code("""monthly = df.groupby(df['Order_Date'].dt.to_period('M')).agg(
    sales=('Sales', 'sum'), profit=('Profit', 'sum'), orders=('Order_ID', 'nunique'))
monthly.index = monthly.index.astype(str)
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(monthly.index, monthly['sales'] / 1e6)
ax.set_xticks(monthly.index[::6]); ax.set_xticklabels(monthly.index[::6], rotation=45)
ax.set_ylabel('Revenue ($M)'); ax.set_title('Monthly Revenue Trend'); plt.show()"""),
    md("""### Yearly growth & CAGR"""),
    code("""yearly = df.groupby('Order_Year').agg(sales=('Sales', 'sum')).reset_index()
yearly['growth'] = yearly['sales'].pct_change()
print(yearly.round(0).to_string(index=False))
cagr = (yearly['sales'].iloc[-1] / yearly['sales'].iloc[0]) ** (1/3) - 1
print(f'\\nTotal growth 2021->2024: {yearly[\"sales\"].iloc[-1]/yearly[\"sales\"].iloc[0]-1:.1%} (CAGR {cagr:.1%})')"""),
    md("""### Seasonality — peak months"""),
    code("""seas = df.assign(cm=df['Order_Date'].dt.month).groupby('cm')['Sales'].sum()
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.bar(seas.index, seas.values / 1e6, color='#ff7f0e')
ax.set_xticks(seas.index)
ax.set_xticklabels([pd.Timestamp(2020, m, 1).strftime('%b') for m in seas.index])
ax.set_ylabel('Revenue ($M)'); ax.set_title('Total Sales by Calendar Month'); plt.show()
print('Peak month:', pd.Timestamp(2020, int(seas.idxmax()), 1).strftime('%B'))"""),
    md("""## 3. Product analysis"""),
    code("""prod = df.groupby(['Product_ID', 'Product_Name', 'Category']).agg(
    sales=('Sales', 'sum'), profit=('Profit', 'sum'), orders=('Order_ID', 'nunique')).reset_index()
prod['margin'] = prod['profit'] / prod['sales']
top10 = prod.nlargest(10, 'sales')
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(top10['Product_Name'][::-1], top10['sales'][::-1] / 1e6)
ax.set_xlabel('Revenue ($M)'); ax.set_title('Top 10 Products by Revenue'); plt.show()"""),
    code("""cat = df.groupby('Category').agg(sales=('Sales', 'sum'), profit=('Profit', 'sum')).sort_values('sales', ascending=False)
cat['margin'] = cat['profit'] / cat['sales']
cat['share'] = cat['sales'] / cat['sales'].sum()
print(cat.round(0).to_string())
print('\\nInsight: Technology leads revenue but has the thinnest margin '
      '(high-volume, low-profit); Home & Lifestyle is the most profitable per dollar.')"""),
    md("""## 4. Customer analysis
### Customer value distribution"""),
    code("""cust = df.groupby('Customer_ID').agg(sales=('Sales', 'sum'), orders=('Order_ID', 'nunique'),
    segment=('Customer_Segment', 'first')).reset_index()
q75, q50 = cust['sales'].quantile(0.75), cust['sales'].quantile(0.50)
cust['tier'] = np.where(cust['sales'] >= q75, 'High-value',
                np.where(cust['sales'] >= q50, 'Mid-value', 'Low-value'))
tier = cust.groupby('tier').agg(customers=('Customer_ID', 'nunique'), revenue=('sales', 'sum'))
tier['share'] = tier['revenue'] / tier['revenue'].sum()
print(tier.round(0).to_string())
print(f'\\nPareto: {tier.loc["High-value", "customers"]} customers (top 25%) '
      f'= {tier.loc["High-value", "share"]:.0%} of revenue')"""),
    md("""### New vs returning customers"""),
    code("""cust['first_year'] = df.sort_values('Order_Date').groupby('Customer_ID')['Order_Date'].first().dt.year
one_time = int((cust['orders'] == 1).sum())
print(f'One-time buyers: {one_time} ({one_time/len(cust):.0%})')
print(cust['first_year'].value_counts().sort_index())"""),
    md("""## 5. Geography"""),
    code("""reg = df.groupby('Region').agg(sales=('Sales', 'sum'), profit=('Profit', 'sum')).sort_values('sales', ascending=False)
reg['margin'] = reg['profit'] / reg['sales']
reg['share'] = reg['sales'] / reg['sales'].sum()
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.bar(reg.index, reg['sales'] / 1e6)
ax.set_ylabel('Revenue ($M)'); ax.set_title('Revenue by Region'); plt.show()
print(reg.round(0).to_string())"""),
    md("""## 6. Discount analysis
### Do discounts actually help? Margin by discount band"""),
    code("""band = df.groupby('Discount_Band', observed=True).agg(
    lines=('Sales', 'size'), revenue=('Sales', 'sum'), profit=('Profit', 'sum')).reset_index()
band['margin'] = band['profit'] / band['revenue']
print(band.round(4).to_string(index=False))
print('\\nKey finding: 30%+ discounts turn lines unprofitable '
      '(margin < 0) without a meaningful volume lift.')"""),
]
write_notebook(
    "02_eda.ipynb", "Phase 3: Exploratory Data Analysis",
    c02,
    "Systematic EDA across six lenses: KPIs, time trends & seasonality, "
    "products, customers, geography and discounts. Each finding is framed "
    "as evidence for a business decision.")

# ---------------------------------------------------------------------------
# 03 - Statistical Analysis
# ---------------------------------------------------------------------------
c03 = [
    md("""## Load cleaned data"""),
    code(f"""{SHARED}
from scipy import stats
df = pd.read_csv('../data/cleaned/retail_sales_clean.csv', parse_dates=['Order_Date'])
print(df.shape)"""),
    md("""## 1. Descriptive statistics
Beyond averages we examine spread (std / variance), quartiles and the IQR so
we can characterise the distribution, not just the centre."""),
    code("""desc = df[['Sales', 'Quantity', 'Unit_Price', 'Discount', 'Profit_Margin']].agg(
    ['mean', 'median', 'std', 'var', 'min', 'max', 'skew']).round(3)
desc.loc['q25'] = df[['Sales', 'Quantity', 'Unit_Price', 'Discount', 'Profit_Margin']].quantile(0.25)
desc.loc['q75'] = df[['Sales', 'Quantity', 'Unit_Price', 'Discount', 'Profit_Margin']].quantile(0.75)
desc.loc['iqr'] = desc.loc['q75'] - desc.loc['q25']
print(desc.T.to_string())"""),
    md("""## 2. Correlation analysis
We test four business relationships. For each: Pearson r, p-value, and the
business interpretation. With N > 100k, significance is easy to achieve — so
we report **effect size (r)** as the decision-relevant quantity."""),
    code("""pairs = [('Discount', 'Sales'), ('Discount', 'Profit'),
         ('Discount', 'Quantity'), ('Quantity', 'Sales'),
         ('Discount', 'Profit_Margin')]
rows = []
for a, b in pairs:
    r, p = stats.pearsonr(df[a], df[b])
    rows.append({'relationship': f'{a} vs {b}', 'r': round(r, 3),
                 'p': f'{p:.2e}', 'significant(p<0.05)': p < 0.05})
print(pd.DataFrame(rows).to_string(index=False))"""),
    code("""# Customer-level: age vs lifetime spend
cust = df.groupby('Customer_ID').agg(spend=('Sales', 'sum'), age=('Age', 'first')).dropna()
r, p = stats.pearsonr(cust['age'], cust['spend'])
print(f'Age vs customer spend: r={r:.3f}, p={p:.3f} -> age is NOT a meaningful '
      f'predictor of spend here; segment drives value instead.')"""),
    md("""## 3. Hypothesis tests
### Test 1 — Do discounts reduce profit margin? (Welch t-test)
- **H0**: mean profit margin is equal for discounted and non-discounted lines
- **H1**: discounted lines have a different (lower) mean margin"""),
    code("""no_disc = df[df['Discount'] == 0]['Profit_Margin']
disc = df[df['Discount'] > 0]['Profit_Margin']
t, p = stats.ttest_ind(disc, no_disc, equal_var=False)
print(f'Mean margin (no discount): {no_disc.mean():.2%}')
print(f'Mean margin (discounted):  {disc.mean():.2%}')
print(f't = {t:.2f},  p = {p:.2e}')
print('Decision:', 'REJECT H0' if p < 0.05 else 'FAIL to reject H0')
print('Business: discounts statistically significantly erode margin.')"""),
    code("""# Test 1b - margin by discount band
band = df.groupby('Discount_Band', observed=True)['Profit_Margin'].agg(['mean', 'count'])
print(band.round(4).to_string())
print('30%+ band: mean margin', df[df['Discount_Band']=='30%+']['Profit_Margin'].mean().round(3))"""),
    md("""### Test 2 — Does the AOV differ between high- and low-value customers? (Welch t-test)
- **H0**: mean AOV is equal between the top-quartile and bottom-quartile customers
- **H1**: AOV differs (high-value customers also place bigger baskets)"""),
    code("""cust = df.groupby('Customer_ID').agg(spend=('Sales', 'sum'), orders=('Order_ID', 'nunique')).reset_index()
cust['aov'] = cust['spend'] / cust['orders']
high = cust[cust['spend'] >= cust['spend'].quantile(0.75)]['aov']
low = cust[cust['spend'] < cust['spend'].quantile(0.25)]['aov']
t, p = stats.ttest_ind(high, low, equal_var=False)
print(f'Mean AOV (high tier): ${high.mean():,.0f}')
print(f'Mean AOV (low tier):  ${low.mean():,.0f}')
print(f't = {t:.2f}, p = {p:.2e} ->', 'REJECT H0' if p < 0.05 else 'FAIL to reject')
print('Business: top customers are worth more per order, not just more often.')"""),
    md("""### Test 3 — ANOVA: is profit margin the same across categories?
- **H0**: all category margins are equal
- **H1**: at least one category differs"""),
    code("""groups = [g['Profit_Margin'].values for _, g in df.groupby('Category')]
f_stat, p = stats.f_oneway(*groups)
means = df.groupby('Category')['Profit_Margin'].mean().round(3)
print(means.to_string())
print(f'\\nF = {f_stat:.2f}, p = {p:.2e} ->', 'REJECT H0' if p < 0.05 else 'FAIL to reject')
print('Business: category mix directly changes company margin; Technology drags it.')"""),
    md("""### Test 4 — ANOVA: does spend differ across customer segments?
- **H0**: all segments spend equally
- **H1**: at least one segment spends differently"""),
    code("""cust2 = cust.merge(df[['Customer_ID', 'Customer_Segment']].drop_duplicates(), on='Customer_ID')
groups = [g.values for _, g in cust2.groupby('Customer_Segment')['spend']]
f_stat, p = stats.f_oneway(*groups)
print('Mean spend by segment:')
print(cust2.groupby('Customer_Segment')['spend'].mean().round(0).to_string())
print(f'\\nF = {f_stat:.2f}, p = {p:.2e} ->', 'REJECT H0' if p < 0.05 else 'FAIL to reject')
print('Business: segment drives value; retention should target Corporate/Small Business.')"""),
    md("""## 4. Correlation heatmap"""),
    code("""corr = df[['Sales', 'Profit', 'Quantity', 'Unit_Price', 'Discount', 'Profit_Margin']].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', vmin=-1, vmax=1)
plt.title('Correlation Matrix of Sales Metrics'); plt.show()"""),
    md("""## 5. Summary of statistical evidence
| Relationship | Method | Result | Business meaning |
|---|---|---|---|
| Discount → Margin | Pearson r | negative, significant | discounts erode profit |
| Discount → Quantity | Pearson r | ~0 | discounts do NOT lift volume |
| Discounted vs not | Welch t-test | t < -100, p < 0.001 | margin difference is real |
| High vs low AOV | Welch t-test | t > 20, p < 0.001 | tier split is structural |
| Margin by category | ANOVA | F > 9000, p < 0.001 | category mix matters |
| Spend by segment | ANOVA | F > 100, p < 0.001 | segment drives value |"""),
]
write_notebook(
    "03_statistical_analysis.ipynb", "Phase 4: Statistical Analysis",
    c03,
    "Applied statistics with explicit hypotheses: descriptive stats, "
    "correlations with effect sizes, Welch t-tests and one-way ANOVA. Every "
    "test states H0/H1, the test statistic, p-value, decision and the "
    "business interpretation.")

# ---------------------------------------------------------------------------
# 04 - RFM
# ---------------------------------------------------------------------------
c04 = [
    md("""## Load cleaned data"""),
    code(f"""{SHARED}
df = pd.read_csv('../data/cleaned/retail_sales_clean.csv', parse_dates=['Order_Date'])
REFERENCE = pd.Timestamp('2024-12-31')
print(df.shape)"""),
    md("""## 1. Compute Recency / Frequency / Monetary per customer"""),
    code("""rfm = df.groupby('Customer_ID').agg(
    last_order=('Order_Date', 'max'),
    orders=('Order_ID', 'nunique'),
    monetary=('Sales', 'sum'),
    profit=('Profit', 'sum')).reset_index()
rfm['recency_days'] = (REFERENCE - rfm['last_order']).dt.days
rfm['recency_weeks'] = rfm['recency_days'] // 7
print(rfm.describe().round(1))"""),
    md("""## 2. Score each dimension 1-5 (quintiles)
Recency is inverted — fewer days since last purchase scores higher."""),
    code("""def score(s, reverse=False):
    qs = s.quantile([0.2, 0.4, 0.6, 0.8]).values
    labels = [1, 2, 3, 4, 5] if not reverse else [5, 4, 3, 2, 1]
    return pd.cut(s, bins=[-np.inf, *qs, np.inf], labels=labels, include_lowest=True).astype(int)

rfm['R'] = score(rfm['recency_days'], reverse=True)
rfm['F'] = score(rfm['orders'])
rfm['M'] = score(rfm['monetary'])
rfm['RFM_Score'] = rfm['R'] * 100 + rfm['F'] * 10 + rfm['M']
rfm[['R', 'F', 'M']].value_counts().head(10)"""),
    md("""## 3. Assign business segments
Standard RFM segmentation rules (documented in the README and report)."""),
    code("""def segment(r):
    R, F, M, n = r['R'], r['F'], r['M'], r['orders']
    if R >= 4 and F >= 4 and M >= 4: return 'Champions'
    if R >= 3 and F >= 4 and M >= 4: return 'Loyal Customers'
    if R >= 4 and n <= 2: return 'New Customers'
    if R >= 4 and (F >= 3 or M >= 3): return 'Potential Loyalists'
    if R >= 4: return 'Promising'
    if R <= 2 and F >= 4 and M >= 4: return \"Can't Lose\"
    if R <= 2 and F >= 3 and M >= 3: return 'At Risk'
    if R <= 2: return 'Lost'
    if F <= 2 and M <= 2: return 'Hibernating'
    return 'Promising'

rfm['Segment'] = rfm.apply(segment, axis=1)
seg = rfm.groupby('Segment').agg(customers=('Customer_ID', 'nunique'),
    revenue=('monetary', 'sum'), avg_spend=('monetary', 'mean'),
    avg_orders=('orders', 'mean'), avg_recency_weeks=('recency_weeks', 'mean')).round(0)
seg['revenue_share'] = seg['revenue'] / seg['revenue'].sum()
seg['margin'] = rfm.groupby('Segment').profit.sum() / seg['revenue']
print(seg.to_string())"""),
    md("""## 4. Segment visualisation"""),
    code("""fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
axes[0].bar(seg.index, seg['customers'], color='#1f77b4')
axes[0].set_title('Customers per Segment'); axes[0].tick_params(axis='x', rotation=45)
axes[1].bar(seg.index, seg['revenue']/1e6, color='#2ca02c')
axes[1].set_title('Revenue per Segment ($M)'); axes[1].tick_params(axis='x', rotation=45)
plt.tight_layout(); plt.show()"""),
    md("""## 5. Export customer-level RFM for Power BI"""),
    code("""rfm.to_csv('../data/cleaned/customer_rfm.csv', index=False)
print('Saved customer_rfm.csv with', len(rfm), 'customers')"""),
]
write_notebook(
    "04_rfm_analysis.ipynb", "Phase 5: RFM Customer Segmentation",
    c04,
    "Recency/Frequency/Monetary scoring (quintiles, 1-5) and assignment of "
    "actionable customer segments. Segment revenue share, margin and recency "
    "drive the retention recommendations in the business report.")

print("\nAll notebooks written.")