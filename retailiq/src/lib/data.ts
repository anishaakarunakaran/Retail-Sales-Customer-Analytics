import type { Transaction, FilterState } from './types';
import { AGE_GROUPS, DISCOUNT_BUCKETS } from './types';

export async function loadDemoData(): Promise<Transaction[]> {
  const res = await fetch('/retail_sales_demo.csv');
  const text = await res.text();
  const Papa = (await import('papaparse')).default;
  const result = Papa.parse(text, { header: true, skipEmptyLines: true, dynamicTyping: true });
  return processRawData(result.data as Transaction[]);
}

export async function loadTestData(): Promise<Transaction[]> {
  const res = await fetch('/retail_sales_test.csv');
  const text = await res.text();
  const Papa = (await import('papaparse')).default;
  const result = Papa.parse(text, { header: true, skipEmptyLines: true, dynamicTyping: true });
  return result.data as Transaction[];
}

export function processRawData(rows: Transaction[]): Transaction[] {
  return rows.map((row) => {
    const age = row.customer_age;
    let ageGroup = 'Unknown';
    if (age !== null && age !== undefined) {
      if (age < 25) ageGroup = AGE_GROUPS[0];
      else if (age < 35) ageGroup = AGE_GROUPS[1];
      else if (age < 45) ageGroup = AGE_GROUPS[2];
      else if (age < 55) ageGroup = AGE_GROUPS[3];
      else if (age < 65) ageGroup = AGE_GROUPS[4];
      else ageGroup = AGE_GROUPS[5];
    }

    const disc = row.discount_percent || 0;
    let discountBucket = DISCOUNT_BUCKETS[0];
    if (disc > 0 && disc <= 10) discountBucket = DISCOUNT_BUCKETS[1];
    else if (disc > 10 && disc <= 20) discountBucket = DISCOUNT_BUCKETS[2];
    else if (disc > 20 && disc <= 30) discountBucket = DISCOUNT_BUCKETS[3];
    else if (disc > 30) discountBucket = DISCOUNT_BUCKETS[4];

    const date = new Date(row.transaction_date);
    const month = date.getMonth() + 1;
    const year = date.getFullYear();
    const quarter = Math.ceil(month / 3);
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const dayOfWeek = days[date.getDay()];

    return {
      ...row,
      age_group: ageGroup,
      discount_bucket: discountBucket,
      customer_type: row.customer_segment === 'Corporate' || row.customer_segment === 'Small Business' ? 'B2B' : 'B2C',
      month,
      year,
      quarter,
      day_of_week: dayOfWeek,
    };
  });
}

export function applyFilters(data: Transaction[], filters: FilterState): Transaction[] {
  if (!filters) return data;
  let result = data;

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    const [start, end] = filters.dateRange;
    result = result.filter((r) => r.transaction_date >= start && r.transaction_date <= end);
  }
  if (filters.regions.length) result = result.filter((r) => filters.regions.includes(r.region));
  if (filters.states.length) result = result.filter((r) => filters.states.includes(r.customer_state));
  if (filters.cities.length) result = result.filter((r) => filters.cities.includes(r.customer_city));
  if (filters.categories.length) result = result.filter((r) => filters.categories.includes(r.category));
  if (filters.subcategories.length) result = result.filter((r) => filters.subcategories.includes(r.subcategory));
  if (filters.brands.length) result = result.filter((r) => filters.brands.includes(r.brand));
  if (filters.customerSegments.length) result = result.filter((r) => filters.customerSegments.includes(r.customer_segment));
  if (filters.genders.length) result = result.filter((r) => filters.genders.includes(r.customer_gender));
  if (filters.ageGroups.length) result = result.filter((r) => r.age_group && filters.ageGroups.includes(r.age_group));
  if (filters.paymentMethods.length) result = result.filter((r) => filters.paymentMethods.includes(r.payment_method));
  if (filters.salesChannels.length) result = result.filter((r) => filters.salesChannels.includes(r.sales_channel));
  if (filters.storeTypes.length) result = result.filter((r) => filters.storeTypes.includes(r.store_type));

  return result;
}

export function getUniqueValues(data: Transaction[], field: keyof Transaction): string[] {
  const vals = new Set<string>();
  data.forEach((r) => {
    const v = r[field];
    if (v !== null && v !== undefined && v !== '') vals.add(String(v));
  });
  return Array.from(vals).sort();
}

export function getFieldStats(data: Transaction[], field: keyof Transaction) {
  const values = data.map((r) => r[field]).filter((v) => v !== null && v !== undefined);
  const numeric = values.filter((v) => typeof v === 'number').map(Number);
  return {
    count: values.length,
    nullCount: data.length - values.length,
    unique: new Set(values).size,
    min: numeric.length ? Math.min(...numeric) : 0,
    max: numeric.length ? Math.max(...numeric) : 0,
    mean: numeric.length ? numeric.reduce((a, b) => a + b, 0) / numeric.length : 0,
    median: numeric.length ? numeric.sort((a, b) => a - b)[Math.floor(numeric.length / 2)] : 0,
  };
}
