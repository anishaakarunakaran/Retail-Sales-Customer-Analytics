export interface Transaction {
  transaction_id: string;
  transaction_date: string;
  customer_id: string;
  customer_name: string;
  customer_age: number | null;
  customer_gender: string;
  customer_city: string;
  customer_state: string;
  customer_segment: string;
  product_id: string;
  product_name: string;
  category: string;
  subcategory: string;
  brand: string;
  unit_price: number;
  quantity: number;
  discount_percent: number;
  sales_amount: number;
  cost_amount: number;
  profit_amount: number;
  payment_method: string;
  sales_channel: string;
  store_id: string;
  store_type: string;
  region: string;
  customer_rating: number;
  returned: boolean;
  order_value?: number;
  age_group?: string;
  discount_bucket?: string;
  customer_type?: string;
  month?: number;
  year?: number;
  quarter?: number;
  day_of_week?: string;
}

export interface FilterState {
  dateRange: [string, string] | null;
  regions: string[];
  states: string[];
  cities: string[];
  categories: string[];
  subcategories: string[];
  brands: string[];
  customerSegments: string[];
  genders: string[];
  ageGroups: string[];
  paymentMethods: string[];
  salesChannels: string[];
  storeTypes: string[];
}

export interface KPI {
  label: string;
  value: number;
  previousValue: number | null;
  change: number | null;
  changePercent: number | null;
  format: 'currency' | 'number' | 'percent' | 'decimal';
  trend?: 'up' | 'down' | 'flat';
}

export interface RFMSegment {
  segment: string;
  customers: number;
  revenue: number;
  avgSpend: number;
  avgFrequency: number;
  avgRecencyDays: number;
  color: string;
}

export interface RFMRow {
  customer_id: string;
  customer_name: string;
  recency: number;
  frequency: number;
  monetary: number;
  r_score: number;
  f_score: number;
  m_score: number;
  rfm_score: string;
  segment: string;
}

export interface DataQualityIssue {
  type: string;
  count: number;
  severity: 'high' | 'medium' | 'low';
  description: string;
}

export interface DataQualityReport {
  totalRows: number;
  validRows: number;
  issues: DataQualityIssue[];
}

export interface StatisticalSummary {
  mean: number;
  median: number;
  mode: number;
  min: number;
  max: number;
  std: number;
  variance: number;
  q1: number;
  q3: number;
  iqr: number;
  count: number;
}

export interface Insight {
  id: string;
  title: string;
  description: string;
  metric: string;
  value: string;
  impact: 'high' | 'medium' | 'low';
  category: string;
}

export interface CleaningOptions {
  missingValues: 'remove' | 'mean' | 'median' | 'mode' | 'ffill' | 'unchanged';
  duplicates: 'remove' | 'keep_first' | 'keep_last';
  outlierMethod: 'iqr' | 'zscore';
  outlierAction: 'detect' | 'remove' | 'cap';
}

export type Granularity = 'day' | 'week' | 'month' | 'quarter' | 'year';

export const DEFAULT_FILTERS: FilterState = {
  dateRange: null,
  regions: [],
  states: [],
  cities: [],
  categories: [],
  subcategories: [],
  brands: [],
  customerSegments: [],
  genders: [],
  ageGroups: [],
  paymentMethods: [],
  salesChannels: [],
  storeTypes: [],
};

export const AGE_GROUPS = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+'];
export const DISCOUNT_BUCKETS = ['None', '1-10%', '11-20%', '21-30%', '30%+'];
