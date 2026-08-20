"""Generate a self-contained, Vercel-ready index.html dashboard from analysis outputs."""
import base64
import json
from pathlib import Path

RESULTS = json.load(open("reports/analysis_results.json", encoding="utf-8"))
RFM = json.load(open("reports/rfm_results.json", encoding="utf-8"))
VIS = Path("visuals")


def img64(name):
    return base64.b64encode((VIS / name).read_bytes()).decode()


def kpi_table():
    k = RESULTS["kpis"]
    return f"""
    <div class="kpis">
      <div class="kpi"><span class="n">${k['total_sales']/1e6:.1f}M</span><span class="l">Total Revenue</span></div>
      <div class="kpi"><span class="n">${k['total_profit']/1e6:.1f}M</span><span class="l">Total Profit</span></div>
      <div class="kpi"><span class="n">{k['overall_profit_margin']*100:.1f}%</span><span class="l">Profit Margin</span></div>
      <div class="kpi"><span class="n">{k['total_orders']:,}</span><span class="l">Orders</span></div>
      <div class="kpi"><span class="n">{k['total_customers']:,}</span><span class="l">Customers</span></div>
      <div class="kpi"><span class="n">${k['avg_order_value']:,.0f}</span><span class="l">Avg Order Value</span></div>
      <div class="kpi"><span class="n">${k['total_sales']:,.0f}</span><span class="l">Exact Revenue</span></div>
    </div>"""


def cat_table():
    rows = "".join(
        f"<tr><td>{c['Category']}</td><td>${c['sales']/1e6:,.1f}M</td>"
        f"<td>{c['sales_share']*100:.0f}%</td><td>{c['margin']*100:.1f}%</td></tr>"
        for c in RESULTS["products"]["category"])
    return (f"<table><tr><th>Category</th><th>Revenue</th><th>Share</th><th>Margin</th></tr>{rows}</table>")


def region_table():
    rows = "".join(
        f"<tr><td>{r['Region']}</td><td>${r['sales']/1e6:,.1f}M</td>"
        f"<td>{r['share']*100:.0f}%</td><td>{r['margin']*100:.1f}%</td></tr>"
        for r in RESULTS["geo"]["region"])
    return (f"<table><tr><th>Region</th><th>Revenue</th><th>Share</th><th>Margin</th></tr>{rows}</table>")


def discount_table():
    rows = "".join(
        f"<tr><td>{b['Discount_Band']}</td><td>${b['sales']/1e6:,.1f}M</td>"
        f"<td>{b['margin']*100:.1f}%</td></tr>"
        for b in RESULTS["discounts"]["bands"])
    return (f"<table><tr><th>Discount Band</th><th>Revenue</th><th>Margin</th></tr>{rows}</table>")


def rfm_table():
    rows = "".join(
        f"<tr><td>{s['Segment']}</td><td>{s['customers']}</td><td>${s['revenue']/1e6:,.1f}M</td>"
        f"<td>{s['revenue_share']*100:.1f}%</td><td>{s['avg_recency_weeks']:.0f}w</td></tr>"
        for s in RFM["segments"])
    return (f"<table><tr><th>RFM Segment</th><th>Customers</th><th>Revenue</th>"
            f"<th>Share</th><th>Avg Recency</th></tr>{rows}</table>")


html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Retail Sales &amp; Customer Analytics — Interactive Report</title>
<style>
  :root {{ --dark:#111827; --accent:#2563eb; --bg:#f5f6f8; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family:'Segoe UI',-apple-system,Arial,sans-serif; margin:0; background:var(--bg); color:#1f2937; line-height:1.5; }}
  .hero {{ background:linear-gradient(135deg,#111827 0%,#1e3a8a 100%); color:#fff; padding:52px 24px 40px; text-align:center; }}
  .hero h1 {{ margin:0 0 10px; font-size:34px; letter-spacing:.5px; }}
  .hero p {{ margin:4px auto; color:#c7d2fe; max-width:760px; }}
  .hero .badges span {{ display:inline-block; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.25); border-radius:999px; padding:4px 14px; margin:8px 4px 0; font-size:13px; }}
  nav {{ position:sticky; top:0; background:#fff; border-bottom:1px solid #e5e7eb; z-index:10; }}
  nav a {{ display:inline-block; padding:12px 16px; color:#374151; text-decoration:none; font-size:14px; font-weight:500; }}
  nav a:hover {{ color:var(--accent); border-bottom:2px solid var(--accent); }}
  main {{ max-width:1180px; margin:0 auto; padding:8px 24px 48px; }}
  section {{ background:#fff; border-radius:12px; padding:22px; margin:22px 0; box-shadow:0 1px 4px rgba(0,0,0,.08); }}
  h2 {{ margin:0 0 6px; font-size:21px; color:var(--dark); }}
  .sub {{ color:#6b7280; font-size:14px; margin:0 0 16px; }}
  .kpis {{ display:flex; flex-wrap:wrap; gap:14px; justify-content:center; }}
  .kpi {{ flex:1 1 150px; max-width:190px; background:#eef2f7; border-radius:10px; padding:16px 10px; text-align:center; }}
  .kpi .n {{ display:block; font-size:24px; font-weight:700; color:var(--accent); }}
  .kpi .l {{ font-size:12px; color:#4b5563; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; align-items:center; }}
  img {{ width:100%; border-radius:8px; border:1px solid #e5e7eb; background:#fff; }}
  table {{ border-collapse:collapse; width:100%; font-size:14px; }}
  th, td {{ border-bottom:1px solid #e5e7eb; padding:9px 10px; text-align:left; }}
  th {{ background:#f3f4f6; font-weight:600; }}
  tr:hover td {{ background:#f9fafb; }}
  .tag {{ display:inline-block; background:#dbeafe; color:#1d4ed8; border-radius:6px; padding:2px 8px; font-size:12px; font-weight:600; }}
  .callout {{ background:#fffbeb; border-left:4px solid #f59e0b; padding:12px 16px; border-radius:6px; font-size:14px; color:#78350f; margin-top:14px; }}
  footer {{ background:var(--dark); color:#9ca3af; text-align:center; padding:24px; font-size:13px; }}
  footer a {{ color:#93c5fd; }}
  @media (max-width:820px) {{ .grid2 {{ grid-template-columns:1fr; }} }}
</style></head><body>

<div class="hero">
  <h1>Retail Sales &amp; Customer Analytics</h1>
  <p>2021–2024 &nbsp;•&nbsp; 108,045 order lines &nbsp;•&nbsp; 33,209 orders &nbsp;•&nbsp; 1,648 customers</p>
  <div class="badges"><span>Python</span><span>Pandas / NumPy</span><span>SciPy / Statsmodels</span><span>SQL (SQLite)</span><span>RFM Segmentation</span><span>Power BI</span></div>
</div>

<nav>
  <a href="#kpis">KPIs</a>
  <a href="#trends">Trends</a>
  <a href="#products">Products</a>
  <a href="#geo">Geography</a>
  <a href="#discounts">Discounts</a>
  <a href="#rfm">Customers / RFM</a>
  <a href="#stats">Statistics</a>
</nav>

<main>
  <section id="kpis"><h2>Headline Numbers</h2>
    <p class="sub">All figures computed from the cleaned dataset — Python and SQL results cross-validate exactly.</p>
    {kpi_table()}
  </section>

  <section id="trends"><h2>Revenue Trends &amp; Seasonality</h2>
    <p class="sub">Revenue grew <b>+22.1%</b> (CAGR 6.9%); December peaks at <b>2.4×</b> July.</p>
    <div class="grid2">
      <div><img src="data:image/png;base64,{img64('monthly_revenue_trend.png')}" alt="Monthly revenue trend"></div>
      <div><img src="data:image/png;base64,{img64('seasonality.png')}" alt="Seasonality"></div>
    </div>
  </section>

  <section id="products"><h2>Product Performance</h2>
    <p class="sub">Technology drives 38% of revenue but only 12.4% margin — a profitability risk.</p>
    <div class="grid2">
      <div>{cat_table()}</div>
      <div><img src="data:image/png;base64,{img64('top10_products.png')}" alt="Top 10 products"></div>
    </div>
  </section>

  <section id="geo"><h2>Geographic Performance</h2>
    <p class="sub">Central is the weakest revenue region (17%) yet has the highest margin (24.0%).</p>
    <div class="grid2">
      <div>{region_table()}</div>
      <div><img src="data:image/png;base64,{img64('revenue_by_region.png')}" alt="Revenue by region"></div>
    </div>
    <img src="data:image/png;base64,{img64('revenue_by_state.png')}" alt="Revenue by state" style="margin-top:16px">
  </section>

  <section id="discounts"><h2>Discount Impact on Profit</h2>
    <p class="sub">Discounts above 30% destroy value — <b>−8.2% margin</b> with zero volume lift.</p>
    <div class="grid2">
      <div>{discount_table()}</div>
      <div><img src="data:image/png;base64,{img64('discount_band_analysis.png')}" alt="Discount bands"></div>
    </div>
    <div class="callout">Correlation of discount with quantity sold: r = 0.004 (p = 0.19, not significant) — deeper discounts do not drive more units.</div>
  </section>

  <section id="rfm"><h2>Customer Value &amp; RFM Segmentation</h2>
    <p class="sub">Top 25% of customers generate 74% of revenue; Champions + Loyal = 80%.</p>
    <div class="grid2">
      <div><img src="data:image/png;base64,{img64('value_tier_revenue.png')}" alt="Value tiers"></div>
      <div><img src="data:image/png;base64,{img64('rfm_segments.png')}" alt="RFM segments"></div>
    </div>
    <div style="margin-top:16px">{rfm_table()}</div>
    <div class="callout">123 at-risk / can't-lose customers represent <b>$4.0M</b> of recoverable annual revenue.</div>
  </section>

  <section id="stats"><h2>Statistical Findings</h2>
    <p class="sub">t-tests, ANOVA and correlation analysis on margin, AOV and segment spend.</p>
    <div class="grid2">
      <div><img src="data:image/png;base64,{img64('correlation_heatmap.png')}" alt="Correlations"></div>
      <div><img src="data:image/png;base64,{img64('category_margin.png')}" alt="Category margin"></div>
    </div>
    <div class="callout">
      Welch t-test: 38.4% margin (no discount) vs 25.3% (discounted), p &lt; 0.001 &nbsp;•&nbsp;
      ANOVA margin by category: F = 9,119, p &lt; 0.001 &nbsp;•&nbsp;
      AOV high vs low tier: t = 24.55, p &lt; 0.001
    </div>
  </section>
</main>

<footer>
  Built with Python • SQL • Statistics • Power BI — open source on
  <a href="https://github.com/anishaakarunakaran/Retail-Sales-Customer-Analytics" target="_blank" rel="noopener">GitHub</a>.
</footer>
</body></html>"""

Path("index.html").write_text(html, encoding="utf-8")
print(f"index.html written ({Path('index.html').stat().st_size/1024:.0f} KB)")