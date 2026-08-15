import React, { useEffect, useState } from 'react';
import { analysis } from '../api/endpoints';

type AnalysisRow = {
  id?: number;
  sample_id?: string;
  metal_recovery?: number | null;
  alumina_recovery?: number | null;
  recovery_category?: string;
  risk_level?: string;
  model_used?: string;
  created_at?: string;
};

export default function Dashboard() {
  const [stats, setStats] = useState({
    total: 0,
    avgMetal: 0,
    avgAlumina: 0,
  });

  const [recentAnalyses, setRecentAnalyses] = useState<AnalysisRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const res = await analysis.history();

      const rows: AnalysisRow[] = Array.isArray(res.data) ? res.data : [];

      const metal = rows
        .map((r) => Number(r.metal_recovery))
        .filter((v) => !Number.isNaN(v));

      const alumina = rows
        .map((r) => Number(r.alumina_recovery))
        .filter((v) => !Number.isNaN(v));

      setStats({
        total: rows.length,
        avgMetal: metal.length
          ? metal.reduce((a, b) => a + b, 0) / metal.length
          : 0,
        avgAlumina: alumina.length
          ? alumina.reduce((a, b) => a + b, 0) / alumina.length
          : 0,
      });

      setRecentAnalyses(rows.slice(-5).reverse());
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRecoveryStyle = (category?: string) => {
    switch (category?.toLowerCase()) {
      case 'high':
        return 'bg-green-100 text-green-700';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700';
      case 'low':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getRiskStyle = (risk?: string) => {
    switch (risk?.toLowerCase()) {
      case 'low':
        return 'bg-green-100 text-green-700';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700';
      case 'high':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="min-h-full bg-slate-50 p-6 md:p-8">

      {/* Header */}
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="mb-1 text-sm font-medium text-blue-600">
            ReAlux Analytics
          </p>

          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Dashboard
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Monitor aluminium dross recovery analysis and model results.
          </p>
        </div>

        <button
          onClick={() => {
            window.location.href = '/new-analysis';
          }}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 hover:shadow-md"
        >
          <span className="text-lg">+</span>
          New Analysis
        </button>
      </div>

      {/* Main Statistics */}
      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">

        {/* Total */}
        <div className="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">
                Total Analyses
              </p>

              <p className="mt-3 text-4xl font-bold text-slate-900">
                {loading ? '—' : stats.total}
              </p>

              <p className="mt-2 text-xs text-slate-400">
                Completed analysis records
              </p>
            </div>

            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-2xl">
              📊
            </div>
          </div>
        </div>

        {/* Metal Recovery */}
        <div className="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">
                Avg Metal Recovery
              </p>

              <p className="mt-3 text-4xl font-bold text-slate-900">
                {loading ? '—' : `${stats.avgMetal.toFixed(1)}%`}
              </p>

              <p className="mt-2 text-xs text-slate-400">
                Average across analyses
              </p>
            </div>

            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-2xl">
              ♻️
            </div>
          </div>

          {!loading && (
            <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-emerald-500 transition-all"
                style={{
                  width: `${Math.min(Math.max(stats.avgMetal, 0), 100)}%`,
                }}
              />
            </div>
          )}
        </div>

        {/* Alumina Recovery */}
        <div className="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">
                Avg Alumina Recovery
              </p>

              <p className="mt-3 text-4xl font-bold text-slate-900">
                {loading ? '—' : `${stats.avgAlumina.toFixed(1)}%`}
              </p>

              <p className="mt-2 text-xs text-slate-400">
                Average across analyses
              </p>
            </div>

            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-50 text-2xl">
              🧪
            </div>
          </div>

          {!loading && (
            <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-purple-500 transition-all"
                style={{
                  width: `${Math.min(Math.max(stats.avgAlumina, 0), 100)}%`,
                }}
              />
            </div>
          )}
        </div>
      </div>

      {/* Overview Section */}
      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">

        {/* Welcome Card */}
        <div className="rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 p-7 text-white shadow-lg lg:col-span-2">
          <div className="max-w-2xl">
            <p className="text-sm font-medium text-blue-100">
              ReAlux Decision Support
            </p>

            <h2 className="mt-2 text-2xl font-bold">
              Aluminium Dross Recovery Analysis
            </h2>

            <p className="mt-3 text-sm leading-6 text-blue-100">
              Analyse material composition, estimate recovery performance,
              evaluate risk, and generate professional PDF reports from your
              analysis results.
            </p>

            <button
              onClick={() => {
                window.location.href = '/new-analysis';
              }}
              className="mt-6 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-blue-700 shadow-sm transition hover:bg-blue-50"
            >
              Start New Analysis →
            </button>
          </div>
        </div>

        {/* Quick Summary */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900">
            Quick Summary
          </h3>

          <div className="mt-5 space-y-4">

            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <span className="text-sm text-slate-500">
                Analyses completed
              </span>

              <span className="font-bold text-slate-900">
                {stats.total}
              </span>
            </div>

            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <span className="text-sm text-slate-500">
                Metal recovery
              </span>

              <span className="font-bold text-emerald-600">
                {stats.avgMetal.toFixed(1)}%
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-500">
                Alumina recovery
              </span>

              <span className="font-bold text-purple-600">
                {stats.avgAlumina.toFixed(1)}%
              </span>
            </div>

          </div>
        </div>
      </div>

      {/* Recent Analyses */}
      <div className="mt-8 rounded-2xl border border-slate-200 bg-white shadow-sm">

        <div className="flex flex-col gap-2 border-b border-slate-100 px-6 py-5 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900">
              Recent Analyses
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Latest analysis records from your account.
            </p>
          </div>

          <button
            onClick={() => {
              window.location.href = '/previous-reports';
            }}
            className="text-sm font-semibold text-blue-600 hover:text-blue-700"
          >
            View All →
          </button>
        </div>

        {loading ? (
          <div className="px-6 py-10 text-center text-sm text-slate-500">
            Loading dashboard...
          </div>
        ) : recentAnalyses.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <div className="text-4xl">📂</div>

            <h3 className="mt-3 font-semibold text-slate-800">
              No analyses yet
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Start your first analysis to see results here.
            </p>

            <button
              onClick={() => {
                window.location.href = '/new-analysis';
              }}
              className="mt-5 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
            >
              Start Analysis
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px]">

              <thead>
                <tr className="border-b border-slate-100 bg-slate-50 text-left">
                  <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Sample
                  </th>

                  <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Metal Recovery
                  </th>

                  <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Alumina
                  </th>

                  <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Category
                  </th>

                  <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Risk
                  </th>
                </tr>
              </thead>

              <tbody>
                {recentAnalyses.map((row, index) => (
                  <tr
                    key={row.id ?? index}
                    className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
                  >
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-800">
                        {row.sample_id || `Analysis ${row.id ?? index + 1}`}
                      </div>

                      <div className="mt-1 text-xs text-slate-400">
                        Analysis #{row.id ?? index + 1}
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <span className="font-semibold text-slate-800">
                        {row.metal_recovery != null
                          ? `${Number(row.metal_recovery).toFixed(2)}%`
                          : '—'}
                      </span>
                    </td>

                    <td className="px-6 py-4">
                      <span className="font-semibold text-slate-800">
                        {row.alumina_recovery != null
                          ? `${Number(row.alumina_recovery).toFixed(2)}%`
                          : '—'}
                      </span>
                    </td>

                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${getRecoveryStyle(
                          row.recovery_category
                        )}`}
                      >
                        {row.recovery_category || 'N/A'}
                      </span>
                    </td>

                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${getRiskStyle(
                          row.risk_level
                        )}`}
                      >
                        {row.risk_level || 'N/A'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>

            </table>
          </div>
        )}
      </div>

      {/* Footer note */}
      <div className="mt-6 rounded-xl border border-blue-100 bg-blue-50 px-5 py-4">
        <p className="text-xs leading-5 text-blue-700">
          <strong>Note:</strong> ReAlux dashboard results are decision-support
          outputs. Safety classifications and process recommendations should
          be verified by qualified personnel and site-specific procedures.
        </p>
      </div>

    </div>
  );
}