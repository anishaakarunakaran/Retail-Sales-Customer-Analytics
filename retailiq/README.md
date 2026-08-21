# RetailIQ - Retail Sales & Customer Analytics Platform

> Turn retail data into actionable business insights.

A production-quality, full-stack retail analytics platform built with Next.js, TypeScript, Tailwind CSS, Recharts, and SQL.js. Deployable on Vercel with zero configuration.

## Features

- **Data Upload** - Drag-and-drop CSV/XLSX upload with automatic schema validation
- **Data Quality** - Detect missing values, duplicates, invalid dates, outliers with IQR/Z-score
- **Data Cleaning** - Remove/fill missing values, deduplicate, cap outliers
- **Interactive Dashboard** - KPI cards with period-over-period comparison, charts, filters
- **Sales Analytics** - Revenue trends, category/region breakdown, channel analysis
- **Product Analytics** - Top/bottom products, profitability matrix, category performance
- **Customer Analytics** - Segments, regions, top customers, repeat rates
- **RFM Segmentation** - Recency/Frequency/Monetary scoring with 9 actionable segments
- **Statistical Analysis** - Descriptive stats, distributions, correlation heatmap
- **Business Insights** - Deterministic analytics engine generating data-driven insights
- **Data Explorer** - Sortable, filterable, searchable data table with column selection
- **Data Playground** - Filter, group, aggregate, sort without changing original data
- **SQL Analytics** - In-browser SQLite (SQL.js) with 12 preset analytical queries
- **Reports** - Executive, Customer, Product, Regional reports with CSV/Excel/PDF export
- **Global Filters** - 13 filter dimensions updating all charts and KPIs dynamically
- **13 Pages** - Overview, Sales, Products, Customers, RFM, Statistics, Insights, Explorer, Playground, Data Quality, SQL, Reports, Settings

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, React 18, Tailwind CSS |
| Charts | Recharts |
| SQL Engine | SQL.js (in-browser SQLite) |
| Data Processing | PapaParse, SheetJS (xlsx) |
| PDF Export | jsPDF + jspdf-autotable |
| Testing | Vitest, Testing Library |
| Deployment | Vercel (static/standalone) |

## Architecture

```
CSV Upload / Demo Data
        |
    Validation (schema check, quality detection)
        |
    Cleaning (missing values, duplicates, outliers)
        |
    Processing (computed fields, age groups, discount buckets)
        |
    Analytics Engine (metrics, RFM, statistics, insights)
        |
    SQL Layer (SQL.js in-browser database)
        |
    Dashboard (13 pages, interactive filters, charts)
        |
    Reports (PDF, CSV, Excel export)
```

## Getting Started

```bash
# Clone
git clone https://github.com/anishaakarunakaran/Retail-Sales-Customer-Analytics.git
cd Retail-Sales-Customer-Analytics/retailiq

# Install
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

Click **"Load Demo Dataset"** in Settings, or the dashboard auto-loads the 32,000-row demo dataset.

## Scripts

| Command | Description |
|---------|------------|
| `npm run dev` | Start development server |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run typecheck` | TypeScript type checking |
| `npm run test` | Run unit tests (Vitest) |

## Demo Datasets

| Dataset | Rows | Description |
|---------|------|-------------|
| `demo-data/retail_sales_demo.csv` | 32,000 | Production-quality demo data |
| `demo-data/retail_sales_test.csv` | 2,015 | Intentionally corrupted test data |

### Regenerate Datasets

```bash
python scripts/generate_dataset.py
python scripts/generate_test_dataset.py
```

## Data Quality Test Dataset

The test dataset includes 118 intentional issues:
- 30 missing values
- 15 duplicate transaction IDs
- 10 invalid dates
- 8 negative quantities
- 5 zero prices
- 10 invalid categories
- 5 missing customer IDs
- 10 inconsistent state names
- 5 extreme price outliers
- 10 unusually high discounts
- 10 incorrect data types

## Project Structure

```
retailiq/
  app/                    # Next.js App Router pages
    page.tsx              # Overview dashboard
    sales/                # Sales analytics
    products/             # Product analytics
    customers/            # Customer analytics
    rfm/                  # RFM segmentation
    statistics/           # Statistical analysis
    insights/             # Business insights
    explorer/             # Data explorer
    playground/           # Data playground
    data-quality/         # Data quality module
    sql/                  # SQL analytics
    reports/              # Report generation
    settings/             # Settings & data management
  components/             # Reusable UI components
  lib/                    # Analytics engine
    types.ts              # TypeScript interfaces
    data.ts               # Data loading & filtering
    metrics.ts            # KPI & metric calculations
    rfm.ts                # RFM segmentation
    stats.ts              # Statistical analysis
    insights.ts           # Business insights engine
    validation.ts         # Data validation & quality
    exports.ts            # CSV, Excel, PDF export
    sql.ts                # SQL.js wrapper
    utils.ts              # Formatting & helpers
    context.tsx           # React context (global state)
  scripts/                # Data generators (Python)
  demo-data/              # Generated datasets
  public/                 # Static assets (demo CSVs)
```

## Deploy to Vercel

1. Push to GitHub
2. Import in Vercel dashboard
3. Framework: Next.js (auto-detected)
4. Deploy

Or CLI:

```bash
npm i -g vercel
vercel --prod
```

## Unit Tests

17 tests covering:
- KPI calculations (revenue, profit, margin, change detection)
- Revenue by period grouping
- Category metrics
- RFM scoring and segmentation
- Descriptive statistics
- Histogram generation
- Correlation matrix
- Schema validation
- Data quality detection
- Data cleaning
- Utility functions

## License

MIT
