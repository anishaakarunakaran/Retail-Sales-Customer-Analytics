import type { Transaction, Insight } from './types';
import { calculateCategoryMetrics, calculateRegionMetrics, calculateTopCustomers, calculateRevenueByPeriod } from './metrics';
import { calculateRFM, aggregateSegments } from './rfm';

export function generateInsights(data: Transaction[]): Insight[] {
  const insights: Insight[] = [];
  let id = 0;

  const byMonth = calculateRevenueByPeriod(data, 'month');
  if (byMonth.length >= 6) {
    const recent3 = byMonth.slice(-3).reduce((a, b) => a + b.revenue, 0);
    const prev3 = byMonth.slice(-6, -3).reduce((a, b) => a + b.revenue, 0);
    const growth = prev3 > 0 ? ((recent3 - prev3) / prev3 * 100) : 0;
    if (Math.abs(growth) > 1) {
      insights.push({ id: `insight-${++id}`, title: `Revenue ${growth > 0 ? 'grew' : 'declined'} ${Math.abs(growth).toFixed(1)}% in the last quarter`, description: `The most recent 3 months generated $${(recent3 / 1e6).toFixed(1)}M, ${growth > 0 ? 'up' : 'down'} from $${(prev3 / 1e6).toFixed(1)}M in the prior quarter.`, metric: 'Quarterly Growth', value: `${growth > 0 ? '+' : ''}${growth.toFixed(1)}%`, impact: Math.abs(growth) > 10 ? 'high' : 'medium', category: 'Revenue' });
    }
  }

  const cats = calculateCategoryMetrics(data);
  if (cats.length > 1) {
    const top = cats[0];
    const low = cats[cats.length - 1];
    const totalCatRev = cats.reduce((a, b) => a + b.revenue, 0);
    insights.push({ id: `insight-${++id}`, title: `${top.category} leads with $${(top.revenue / 1e6).toFixed(1)}M in revenue`, description: `${top.category} accounts for ${((top.revenue / totalCatRev) * 100).toFixed(0)}% of total revenue with a ${((top.profit / top.revenue) * 100).toFixed(1)}% margin. ${low.category} is the lowest performer at $${(low.revenue / 1e6).toFixed(1)}M.`, metric: 'Category Revenue', value: `$${(top.revenue / 1e6).toFixed(1)}M`, impact: 'high', category: 'Products' });

    const bestMargin = cats.reduce((a, b) => a.margin > b.margin ? a : b);
    const worstMargin = cats.reduce((a, b) => a.margin < b.margin ? a : b);
    insights.push({ id: `insight-${++id}`, title: `${bestMargin.category} has the highest margin at ${(bestMargin.margin * 100).toFixed(1)}%`, description: `While ${bestMargin.category} leads in profitability, ${worstMargin.category} lags at ${(worstMargin.margin * 100).toFixed(1)}% margin.`, metric: 'Margin Gap', value: `${((bestMargin.margin - worstMargin.margin) * 100).toFixed(1)}pp`, impact: 'medium', category: 'Products' });
  }

  const topCustomers = calculateTopCustomers(data);
  const totalRevenue = data.reduce((a, b) => a + (b.sales_amount || 0), 0);
  const top10Pct = Math.ceil(topCustomers.length * 0.1);
  const top10Rev = topCustomers.slice(0, top10Pct).reduce((a, b) => a + b.revenue, 0);
  const concentration = totalRevenue > 0 ? (top10Rev / totalRevenue * 100) : 0;
  if (concentration > 30) {
    insights.push({ id: `insight-${++id}`, title: `Top 10% of customers generate ${concentration.toFixed(1)}% of revenue`, description: `${top10Pct} customers contribute $${(top10Rev / 1e6).toFixed(1)}M of total $${(totalRevenue / 1e6).toFixed(1)}M revenue.`, metric: 'Customer Concentration', value: `${concentration.toFixed(1)}%`, impact: 'high', category: 'Customers' });
  }

  const discounted = data.filter((r) => r.discount_percent > 0);
  const nonDiscounted = data.filter((r) => r.discount_percent === 0);
  if (discounted.length > 0 && nonDiscounted.length > 0) {
    const discRev = discounted.reduce((a, b) => a + b.sales_amount, 0);
    const discProfit = discounted.reduce((a, b) => a + b.profit_amount, 0);
    const noDiscRev = nonDiscounted.reduce((a, b) => a + b.sales_amount, 0);
    const noDiscProfit = nonDiscounted.reduce((a, b) => a + b.profit_amount, 0);
    const discMargin = discRev > 0 ? discProfit / discRev : 0;
    const noDiscMargin = noDiscRev > 0 ? noDiscProfit / noDiscRev : 0;
    if (noDiscMargin > discMargin) {
      insights.push({ id: `insight-${++id}`, title: `Discounted orders have ${(noDiscMargin - discMargin).toFixed(1)}pp lower margin`, description: `Non-discounted margin is ${(noDiscMargin * 100).toFixed(1)}% vs ${(discMargin * 100).toFixed(1)}% for discounted. ${discounted.length} of ${data.length} orders carry a discount.`, metric: 'Discount Impact', value: `${((noDiscMargin - discMargin) * 100).toFixed(1)}pp`, impact: 'high', category: 'Discounts' });
    }
  }

  const regions = calculateRegionMetrics(data);
  if (regions.length > 1) {
    const topReg = regions[0];
    const lowReg = regions[regions.length - 1];
    insights.push({ id: `insight-${++id}`, title: `${topReg.region} leads in revenue at $${(topReg.revenue / 1e6).toFixed(1)}M`, description: `${topReg.region} generates $${(topReg.revenue / 1e6).toFixed(1)}M from ${topReg.customers} customers. ${lowReg.region} is the smallest at $${(lowReg.revenue / 1e6).toFixed(1)}M.`, metric: 'Regional Revenue', value: `$${(topReg.revenue / 1e6).toFixed(1)}M`, impact: 'medium', category: 'Geography' });
  }

  const rfm = calculateRFM(data);
  const segments = aggregateSegments(rfm);
  const champions = segments.find((s) => s.segment === 'Champions');
  const atRisk = segments.find((s) => s.segment === 'At Risk') || segments.find((s) => s.segment === "Can't Lose");
  if (champions && atRisk) {
    insights.push({ id: `insight-${++id}`, title: `${champions.customers} Champions generate $${(champions.revenue / 1e6).toFixed(1)}M`, description: `Champions have an avg spend of $${Math.round(champions.avgSpend).toLocaleString()}. ${atRisk.customers} at-risk customers represent $${(atRisk.revenue / 1e6).toFixed(1)}M in recoverable revenue.`, metric: 'RFM Value', value: `$${(champions.revenue / 1e6).toFixed(1)}M`, impact: 'high', category: 'Customers' });
  }

  const seasonal = byMonth.filter((m) => m.period.endsWith('-12'));
  if (seasonal.length > 0) {
    const avgAll = totalRevenue / Math.max(byMonth.length, 1);
    const avgDec = seasonal.reduce((a, b) => a + b.revenue, 0) / seasonal.length;
    if (avgAll > 0) {
      insights.push({ id: `insight-${++id}`, title: `December revenue is ${(avgDec / avgAll).toFixed(1)}x the monthly average`, description: `December generates $${(avgDec / 1e6).toFixed(1)}M on average vs $${(avgAll / 1e6).toFixed(1)}M monthly average. Seasonal planning is critical.`, metric: 'Seasonal Peak', value: `${(avgDec / avgAll).toFixed(1)}x`, impact: 'medium', category: 'Seasonality' });
    }
  }

  return insights;
}
