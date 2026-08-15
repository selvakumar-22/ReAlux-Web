import React, { useEffect, useState } from 'react';
import { analysis } from '../api/endpoints';

interface AnalysisRow {
  id?: number;
  model_used?: string;
  model_type?: string;

  r2_metal?: number | null;
  mae_metal?: number | null;
  rmse_metal?: number | null;

  r2_alumina?: number | null;
  mae_alumina?: number | null;
  rmse_alumina?: number | null;
}

export default function ModelPerformance() {
  const [rows, setRows] = useState<AnalysisRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadPerformance = async () => {
      try {
        const res = await analysis.history();
        setRows(res.data || []);
      } catch (err) {
        console.error(err);
        setError('Unable to load model performance data.');
      } finally {
        setLoading(false);
      }
    };

    loadPerformance();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <div className="text-gray-500 text-lg">
          Loading model performance...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-5 rounded-xl">
        {error}
      </div>
    );
  }

  const validRows = rows.filter(
    (row) =>
      row.r2_metal != null ||
      row.r2_alumina != null ||
      row.mae_metal != null ||
      row.mae_alumina != null
  );

  const average = (values: (number | null | undefined)[]) => {
    const valid = values.filter(
      (v): v is number => typeof v === 'number' && !isNaN(v)
    );

    if (!valid.length) return null;

    return valid.reduce((a, b) => a + b, 0) / valid.length;
  };

  const avgR2Metal = average(validRows.map((r) => r.r2_metal));
  const avgMAEMetal = average(validRows.map((r) => r.mae_metal));
  const avgRMSEMetal = average(validRows.map((r) => r.rmse_metal));

  const avgR2Alumina = average(validRows.map((r) => r.r2_alumina));
  const avgMAEAlumina = average(validRows.map((r) => r.mae_alumina));
  const avgRMSEAlumina = average(validRows.map((r) => r.rmse_alumina));

  const formatValue = (value: number | null) => {
    if (value == null || isNaN(value)) return 'N/A';
    return value.toFixed(3);
  };

  return (
    <div className="space-y-8">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-semibold text-blue-600 mb-1">
            ReAlux Analytics
          </div>

          <h1 className="text-3xl font-bold text-gray-900">
            Model Performance
          </h1>

          <p className="text-gray-500 mt-2">
            View machine learning performance metrics from completed analyses.
          </p>
        </div>

        <div className="bg-blue-50 px-5 py-3 rounded-xl">
          <div className="text-sm text-blue-600">
            Analyses with metrics
          </div>

          <div className="text-2xl font-bold text-blue-800">
            {validRows.length}
          </div>
        </div>
      </div>

      {/* No metrics */}
      {validRows.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-10 text-center">
          <div className="text-5xl mb-4">📊</div>

          <h2 className="text-xl font-semibold text-gray-800">
            No model metrics available
          </h2>

          <p className="text-gray-500 mt-2">
            Run an analysis with sufficient dataset samples to generate
            model performance metrics.
          </p>
        </div>
      ) : (
        <>
          {/* Metal Recovery */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Metal Recovery Model
              </h2>

              <p className="text-gray-500 text-sm mt-1">
                Average performance across completed analyses
              </p>
            </div>

            <div className="grid grid-cols-3 gap-5">

              <div className="bg-blue-50 rounded-xl p-5">
                <div className="text-sm text-gray-500">
                  R² Score
                </div>

                <div className="text-3xl font-bold text-blue-700 mt-2">
                  {formatValue(avgR2Metal)}
                </div>

                <p className="text-xs text-gray-400 mt-2">
                  Higher is better
                </p>
              </div>

              <div className="bg-green-50 rounded-xl p-5">
                <div className="text-sm text-gray-500">
                  MAE
                </div>

                <div className="text-3xl font-bold text-green-700 mt-2">
                  {formatValue(avgMAEMetal)}
                </div>

                <p className="text-xs text-gray-400 mt-2">
                  Lower is better
                </p>
              </div>

              <div className="bg-purple-50 rounded-xl p-5">
                <div className="text-sm text-gray-500">
                  RMSE
                </div>

                <div className="text-3xl font-bold text-purple-700 mt-2">
                  {formatValue(avgRMSEMetal)}
                </div>

                <p className="text-xs text-gray-400 mt-2">
                  Lower is better
                </p>
              </div>

            </div>
          </div>

          {/* Alumina Recovery */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Alumina Recovery Model
              </h2>

              <p className="text-gray-500 text-sm mt-1">
                Average performance across completed analyses
              </p>
            </div>

            <div className="grid grid-cols-3 gap-5">

              <div className="bg-blue-50 rounded-xl p-5">
                <div className="text-sm text-gray-500">
                  R² Score
                </div>

                <div className="text-3xl font-bold text-blue-700 mt-2">
                  {formatValue(avgR2Alumina)}
                </div>

                <p className="text-xs text-gray-400 mt-2">
                  Higher is better
                </p>
              </div>

              <div className="bg-green-50 rounded-xl p-5">
                <div className="text-sm text-gray-500">
                  MAE
                </div>

                <div className="text-3xl font-bold text-green-700 mt-2">
                  {formatValue(avgMAEAlumina)}
                </div>

                <p className="text-xs text-gray-400 mt-2">
                  Lower is better
                </p>
              </div>

              <div className="bg-purple-50 rounded-xl p-5">
                <div className="text-sm text-gray-500">
                  RMSE
                </div>

                <div className="text-3xl font-bold text-purple-700 mt-2">
                  {formatValue(avgRMSEAlumina)}
                </div>

                <p className="text-xs text-gray-400 mt-2">
                  Lower is better
                </p>
              </div>

            </div>
          </div>

          {/* Analysis History */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">

            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  Analysis Performance History
                </h2>

                <p className="text-sm text-gray-500 mt-1">
                  Metrics recorded for each completed analysis
                </p>
              </div>
            </div>

            <div className="overflow-x-auto">

              <table className="min-w-full">

                <thead>
                  <tr className="border-b border-gray-200">

                    <th className="text-left px-4 py-3 text-sm font-semibold text-gray-600">
                      Analysis
                    </th>

                    <th className="text-left px-4 py-3 text-sm font-semibold text-gray-600">
                      Model
                    </th>

                    <th className="text-center px-4 py-3 text-sm font-semibold text-gray-600">
                      Metal R²
                    </th>

                    <th className="text-center px-4 py-3 text-sm font-semibold text-gray-600">
                      Metal MAE
                    </th>

                    <th className="text-center px-4 py-3 text-sm font-semibold text-gray-600">
                      Alumina R²
                    </th>

                    <th className="text-center px-4 py-3 text-sm font-semibold text-gray-600">
                      Alumina MAE
                    </th>

                  </tr>
                </thead>

                <tbody>

                  {validRows.map((row, index) => (

                    <tr
                      key={row.id ?? index}
                      className="border-b border-gray-100 hover:bg-gray-50"
                    >

                      <td className="px-4 py-4 font-medium text-gray-800">
                        #{row.id ?? index + 1}
                      </td>

                      <td className="px-4 py-4">
                        <div className="font-medium text-gray-800">
                          {row.model_used || 'Unknown'}
                        </div>

                        <div className="text-xs text-gray-400">
                          {row.model_type || '—'}
                        </div>
                      </td>

                      <td className="px-4 py-4 text-center">
                        {formatValue(row.r2_metal ?? null)}
                      </td>

                      <td className="px-4 py-4 text-center">
                        {formatValue(row.mae_metal ?? null)}
                      </td>

                      <td className="px-4 py-4 text-center">
                        {formatValue(row.r2_alumina ?? null)}
                      </td>

                      <td className="px-4 py-4 text-center">
                        {formatValue(row.mae_alumina ?? null)}
                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>
          </div>

          {/* Metric explanation */}
          <div className="bg-gray-50 rounded-2xl border border-gray-200 p-6">

            <h2 className="text-lg font-bold text-gray-900 mb-4">
              Metric Guide
            </h2>

            <div className="grid grid-cols-3 gap-6">

              <div>
                <div className="font-semibold text-gray-800">
                  R² Score
                </div>

                <p className="text-sm text-gray-500 mt-1">
                  Measures how well the model explains variation in the
                  target. Values closer to 1 indicate better performance.
                </p>
              </div>

              <div>
                <div className="font-semibold text-gray-800">
                  MAE
                </div>

                <p className="text-sm text-gray-500 mt-1">
                  Mean Absolute Error measures the average prediction error.
                  Lower values indicate better accuracy.
                </p>
              </div>

              <div>
                <div className="font-semibold text-gray-800">
                  RMSE
                </div>

                <p className="text-sm text-gray-500 mt-1">
                  Root Mean Squared Error gives more weight to larger
                  prediction errors. Lower is better.
                </p>
              </div>

            </div>

          </div>
        </>
      )}

    </div>
  );
}