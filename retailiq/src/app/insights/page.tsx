'use client';
import { useData } from '@/lib/context';
import { generateInsights } from '@/lib/insights';
import { classNames } from '@/lib/utils';

export default function InsightsPage() {
  const { filteredData } = useData();
  if (filteredData.length === 0) return <div className="text-center py-20 text-gray-500">Loading...</div>;

  const insights = generateInsights(filteredData);
  const impactColors = { high: 'border-red-200 bg-red-50', medium: 'border-amber-200 bg-amber-50', low: 'border-gray-200 bg-gray-50' };
  const impactBadge = { high: 'bg-red-100 text-red-700', medium: 'bg-amber-100 text-amber-700', low: 'bg-gray-100 text-gray-600' };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Business Insights</h2>
      <p className="text-sm text-gray-500">Deterministic analytics engine generating insights from actual dataset calculations.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {insights.map((insight) => (
          <div key={insight.id} className={classNames('border rounded-lg p-4', impactColors[insight.impact])}>
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-sm font-semibold text-gray-900">{insight.title}</h3>
              <span className={classNames('text-xs font-medium px-2 py-0.5 rounded-full', impactBadge[insight.impact])}>{insight.impact}</span>
            </div>
            <p className="text-sm text-gray-600 mb-2">{insight.description}</p>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span>Metric: <strong>{insight.metric}</strong></span>
              <span>Value: <strong>{insight.value}</strong></span>
              <span className="ml-auto bg-white px-2 py-0.5 rounded border">{insight.category}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
