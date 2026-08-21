import type { Transaction, KPI } from './types';
import { calculateChange } from './utils';

function sum(data: Transaction[], field: keyof Transaction): number {
  return data.reduce((acc, r) => acc + (Number(r[field]) || 0), 0);
}

function uniqueCount(data: Transaction[], field: keyof Transaction): number {
  return new Set(data.map((r) => r[field])).size;
}

function orders(data: Transaction[]): number {
  return new Set(data.map((r) => r.transaction_id)).size;
}

function buildKPI(label: string, value: number, prev: number | null, format: KPI['format']): KPI {
  if (prev !== null) {
    const { percent } = calculateChange(value, prev);
    return { label, value, previousValue: prev, change: value - prev, changePercent: percent, format, trend: percent > 0 ? 'up' : percent < 0 ? 'down' : 'flat' };
  }
  return { label, value, previousValue: null, change: null, changePercent: null, format };
}

export function calculateKPIs(data: Transaction[], previousData?: Transaction[]): KPI[] {
  const totalRevenue = sum(data, 'sales_amount');
  const totalProfit = sum(data, 'profit_amount');
  const totalOrders = orders(data);
  const totalCustomers = uniqueCount(data, 'customer_id');
  const returnedCount = data.filter((r) => r.returned === true || String(r.returned) === 'True' || String(r.returned) === 'true').length;

  const prevRevenue = previousData ? sum(previousData, 'sales_amount') : null;
  const prevProfit = previousData ? sum(previousData, 'profit_amount') : null;
  const prevOrders = previousData ? orders(previousData) : null;
  const prevCustomers = previousData ? uniqueCount(previousData, 'customer_id') : null;

  const margin = totalRevenue > 0 ? totalProfit / totalRevenue : 0;
  const aov = totalOrders > 0 ? totalRevenue / totalOrders : 0;
  const repeatRate = totalCustomers > 0 ? 1 - (new Set(data.filter((r) => data.filter((x) => x.customer_id === r.customer_id).length === 1).map((r) => r.customer_id)).size / totalCustomers) : 0;
  const returnRate = data.length > 0 ? returnedCount / data.length : 0;

  return [
    buildKPI('Total Revenue', totalRevenue, prevRevenue, 'currency'),
    buildKPI('Total Profit', totalProfit, prevProfit, 'currency'),
    buildKPI('Profit Margin', margin, previousData ? (sum(previousData, 'profit_amount') / (sum(previousData, 'sales_amount') || 1)) : null, 'percent'),
    buildKPI('Total Orders', totalOrders, prevOrders, 'number'),
    buildKPI('Average Order Value', aov, previousData && prevOrders ? sum(previousData, 'sales_amount') / prevOrders : null, 'currency'),
    buildKPI('Total Customers', totalCustomers, prevCustomers, 'number'),
    buildKPI('Repeat Customer Rate', repeatRate, null, 'percent'),
    buildKPI('Return Rate', returnRate, null, 'percent'),
  ];
}

export function calculateRevenueByPeriod(data: Transaction[], period: 'day' | 'week' | 'month' | 'quarter' | 'year') {
  const map = new Map<string, { revenue: number; profit: number; orders: Set<string>; quantity: number }>();

  data.forEach((r) => {
    const d = new Date(r.transaction_date);
    let key = '';
    if (period === 'day') key = r.transaction_date;
    else if (period === 'week') { const start = new Date(d); start.setDate(d.getDate() - d.getDay()); key = start.toISOString().slice(0, 10); }
    else if (period === 'month') key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
    else if (period === 'quarter') key = `${d.getFullYear()}-Q${Math.ceil((d.getMonth() + 1) / 3)}`;
    else key = String(d.getFullYear());

    if (!map.has(key)) map.set(key, { revenue: 0, profit: 0, orders: new Set(), quantity: 0 });
    const entry = map.get(key)!;
    entry.revenue += r.sales_amount || 0;
    entry.profit += r.profit_amount || 0;
    entry.orders.add(r.transaction_id);
    entry.quantity += r.quantity || 0;
  });

  return Array.from(map.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([period, v]) => ({ period, revenue: v.revenue, profit: v.profit, orders: v.orders.size, quantity: v.quantity }));
}

export function calculateCategoryMetrics(data: Transaction[]) {
  const map = new Map<string, { revenue: number; profit: number; quantity: number; orders: Set<string>; ratings: number[] }>();
  data.forEach((r) => {
    if (!map.has(r.category)) map.set(r.category, { revenue: 0, profit: 0, quantity: 0, orders: new Set(), ratings: [] });
    const e = map.get(r.category)!;
    e.revenue += r.sales_amount || 0;
    e.profit += r.profit_amount || 0;
    e.quantity += r.quantity || 0;
    e.orders.add(r.transaction_id);
    if (r.customer_rating) e.ratings.push(r.customer_rating);
  });
  return Array.from(map.entries())
    .map(([category, v]) => ({
      category, revenue: v.revenue, profit: v.profit, quantity: v.quantity, margin: v.revenue > 0 ? v.profit / v.revenue : 0, orders: v.orders.size, avgRating: v.ratings.length ? v.ratings.reduce((a, b) => a + b, 0) / v.ratings.length : 0,
    }))
    .sort((a, b) => b.revenue - a.revenue);
}

export function calculateRegionMetrics(data: Transaction[]) {
  const map = new Map<string, { revenue: number; profit: number; customers: Set<string>; orders: Set<string> }>();
  data.forEach((r) => {
    if (!map.has(r.region)) map.set(r.region, { revenue: 0, profit: 0, customers: new Set(), orders: new Set() });
    const e = map.get(r.region)!;
    e.revenue += r.sales_amount || 0;
    e.profit += r.profit_amount || 0;
    e.customers.add(r.customer_id);
    e.orders.add(r.transaction_id);
  });
  return Array.from(map.entries())
    .map(([region, v]) => ({ region, revenue: v.revenue, profit: v.profit, customers: v.customers.size, margin: v.revenue > 0 ? v.profit / v.revenue : 0, orders: v.orders.size }))
    .sort((a, b) => b.revenue - a.revenue);
}

export function calculateSubcategoryMetrics(data: Transaction[]) {
  const map = new Map<string, { revenue: number; profit: number; quantity: number; orders: Set<string>; category: string }>();
  data.forEach((r) => {
    const key = r.subcategory;
    if (!map.has(key)) map.set(key, { revenue: 0, profit: 0, quantity: 0, orders: new Set(), category: r.category });
    const e = map.get(key)!;
    e.revenue += r.sales_amount || 0;
    e.profit += r.profit_amount || 0;
    e.quantity += r.quantity || 0;
    e.orders.add(r.transaction_id);
  });
  return Array.from(map.entries())
    .map(([subcategory, v]) => ({ subcategory, category: v.category, revenue: v.revenue, profit: v.profit, quantity: v.quantity, margin: v.revenue > 0 ? v.profit / v.revenue : 0, orders: v.orders.size }))
    .sort((a, b) => b.revenue - a.revenue);
}

export function calculatePaymentMetrics(data: Transaction[]) {
  const map = new Map<string, { revenue: number; orders: Set<string> }>();
  data.forEach((r) => {
    if (!map.has(r.payment_method)) map.set(r.payment_method, { revenue: 0, orders: new Set() });
    const e = map.get(r.payment_method)!;
    e.revenue += r.sales_amount || 0;
    e.orders.add(r.transaction_id);
  });
  return Array.from(map.entries())
    .map(([method, v]) => ({ method, revenue: v.revenue, orders: v.orders.size }))
    .sort((a, b) => b.revenue - a.revenue);
}

export function calculateChannelMetrics(data: Transaction[]) {
  const map = new Map<string, { revenue: number; orders: Set<string>; profit: number }>();
  data.forEach((r) => {
    if (!map.has(r.sales_channel)) map.set(r.sales_channel, { revenue: 0, orders: new Set(), profit: 0 });
    const e = map.get(r.sales_channel)!;
    e.revenue += r.sales_amount || 0;
    e.profit += r.profit_amount || 0;
    e.orders.add(r.transaction_id);
  });
  return Array.from(map.entries()).map(([channel, v]) => ({ channel, revenue: v.revenue, orders: v.orders.size, profit: v.profit, margin: v.revenue > 0 ? v.profit / v.revenue : 0 }));
}

export function calculateProductMetrics(data: Transaction[]) {
  const map = new Map<string, { productName: string; category: string; subcategory: string; brand: string; revenue: number; profit: number; quantity: number; orders: Set<string>; ratings: number[]; returned: number }>();
  data.forEach((r) => {
    if (!map.has(r.product_id)) map.set(r.product_id, { productName: r.product_name, category: r.category, subcategory: r.subcategory, brand: r.brand, revenue: 0, profit: 0, quantity: 0, orders: new Set(), ratings: [], returned: 0 });
    const e = map.get(r.product_id)!;
    e.revenue += r.sales_amount || 0;
    e.profit += r.profit_amount || 0;
    e.quantity += r.quantity || 0;
    e.orders.add(r.transaction_id);
    if (r.customer_rating) e.ratings.push(r.customer_rating);
    if (r.returned === true || String(r.returned) === 'True' || String(r.returned) === 'true') e.returned++;
  });
  return Array.from(map.entries())
    .map(([product_id, v]) => ({ product_id, productName: v.productName, category: v.category, subcategory: v.subcategory, brand: v.brand, revenue: v.revenue, profit: v.profit, quantity: v.quantity, orders: v.orders.size, margin: v.revenue > 0 ? v.profit / v.revenue : 0, avgRating: v.ratings.length ? v.ratings.reduce((a, b) => a + b, 0) / v.ratings.length : 0, returnRate: v.orders.size > 0 ? v.returned / v.orders.size : 0 }))
    .sort((a, b) => b.revenue - a.revenue);
}

export function calculateTopCustomers(data: Transaction[]) {
  const map = new Map<string, { name: string; segment: string; region: string; revenue: number; orders: Set<string>; avgRating: number[] }>();
  data.forEach((r) => {
    if (!map.has(r.customer_id)) map.set(r.customer_id, { name: r.customer_name, segment: r.customer_segment, region: r.region, revenue: 0, orders: new Set(), avgRating: [] });
    const e = map.get(r.customer_id)!;
    e.revenue += r.sales_amount || 0;
    e.orders.add(r.transaction_id);
    if (r.customer_rating) e.avgRating.push(r.customer_rating);
  });
  return Array.from(map.entries())
    .map(([customer_id, v]) => ({ customer_id, name: v.name, segment: v.segment, region: v.region, revenue: v.revenue, orders: v.orders.size, avgRating: v.avgRating.length ? v.avgRating.reduce((a, b) => a + b, 0) / v.avgRating.length : 0 }))
    .sort((a, b) => b.revenue - a.revenue);
}

export function calculateStateMetrics(data: Transaction[]) {
  const map = new Map<string, { revenue: number; profit: number; customers: Set<string>; region: string }>();
  data.forEach((r) => {
    if (!map.has(r.customer_state)) map.set(r.customer_state, { revenue: 0, profit: 0, customers: new Set(), region: r.region });
    const e = map.get(r.customer_state)!;
    e.revenue += r.sales_amount || 0;
    e.profit += r.profit_amount || 0;
    e.customers.add(r.customer_id);
  });
  return Array.from(map.entries())
    .map(([state, v]) => ({ state, region: v.region, revenue: v.revenue, profit: v.profit, customers: v.customers.size, margin: v.revenue > 0 ? v.profit / v.revenue : 0 }))
    .sort((a, b) => b.revenue - a.revenue);
}
