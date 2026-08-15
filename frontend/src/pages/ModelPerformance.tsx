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

  metal_recovery?: number | null;
  alumina_recovery?: number | null;
}

export default function ModelPerformance() {
  const [rows, setRows] = useState<AnalysisRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadPerformance = async () => {
      try {
        setLoading(true);
        setError('');

        const res = await analysis.history();

        const data = Array.isArray(res.data) ? res.data : [];

        setRows(data);
      } catch (err) {
        console.error('Failed to load model performance:', err);
        setError('Unable to load model performance data.');
      } finally {
        setLoading(false);
      }
    };

    loadPerformance();
  }, []);

  if (loading) {
    return (
      <div className="p-6">
        <div className="bg-white rounded-xl shadow p-8 text-center">
          <div className="text-lg font-medium text-gray-700">
            Loading model performance...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-6">
          {error}
        </div>
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
      (value): value is number =>
        value !== null &&
        value !== undefined &&
        !Number.isNaN(Number(value))
    );

    if (valid.length === 0) return null;

    return valid.reduce((sum, value) => sum + Number(value), 0) / valid.length;
  };

  const avgR2Metal = average(validRows.map((r) => r.r2_metal));
  const avgMaeMetal = average(validRows.map((r) => r.mae_metal));
  const avgRmseMetal = average(validRows.map((r) => r.rmse_metal));

  const avgR2Alumina = average(validRows.map((r) => r.r2_alumina));
  const avgMaeAlumina = average(validRows.map((r) => r.mae_alumina));
  const avgRmseAlumina = average(validRows.map((r) => r.rmse_alumina));

  const latest = rows.length > 0 ? rows[rows.length - 1] : null;

  const formatValue = (value: number | null | undefined, digits = 3) => {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return '—';
    }

    return Number(value).toFixed(digits);
  };

  const getR2Width = (value: number | null | undefined) => {
    if (value == null || Number.isNaN(Number(value))) return '0%';

    const percentage = Math.max(0, Math.min(100, Number(value) * 100));

    return `${percentage}%`;
  };

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-blue-600 mb-1">
            ReAlux Machine Learning
          </p>

          <h1 className="text-3xl font-bold text-gray-900">
            Model Performance
          </h1>

          <p className="text-gray-500 mt-2">
            Evaluate model accuracy and prediction performance from completed
            analyses.
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

      {/* Latest Model */}
      {latest && (
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl shadow-lg p-6">
          <div className="text-sm opacity-80">
            Latest Analysis Model
          </div>

          <div className="text-2xl font-bold mt-1">
            {latest.model_used || 'Model information unavailable'}
          </div>

          <div className="mt-2 text-sm opacity-90">
            Model type: {latest.model_type || '—'}
          </div>
        </div>
      )}

      {/* Metal Recovery Metrics */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Metal Recovery Model
        </h2>

        <div className="grid grid-cols-3 gap-6">

          {/* R2 */}
          <div className="bg-white rounded-2xl shadow p-6">
            <div className="flex justify-between items-start">
              <div>
                <div className="text-sm text-gray-500">
                  Average R²
                </div>

                <div className="text-3xl font-bold text-gray-900 mt-2">
                  {formatValue(avgR2Metal)}
                </div>
              </div>

              <div className="bg-green-100 text-green-700 px-3 py-2 rounded-lg">
                R²
              </div>
            </div>

            <div className="mt-5 h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 rounded-full"
                style={{ width: getR2Width(avgR2Metal) }}
              />
            </div>

            <p className="text-xs text-gray-400 mt-2">
              Higher is better
            </p>
          </div>

          {/* MAE */}
          <div className="bg-white rounded-2xl shadow p-6">
            <div className="flex justify-between items-start">
              <div>
                <div className="text-sm text-gray-500">
                  Average MAE
                </div>

                <div className="text-3xl font-bold text-gray-900 mt-2">
                  {formatValue(avgMaeMetal)}
                </div>
              </div>

              <div className="bg-purple-100 text-purple-700 px-3 py-2 rounded-lg">
                MAE
              </div>
            </div>

            <p className="text-xs text-gray-400 mt-5">
              Mean Absolute Error
            </p>
          </div>

          {/* RMSE */}
          <div className="bg-white rounded-2xl shadow p-6">
            <div className="flex justify-between items-start">
              <div>
                <div className="text-sm text-gray-500">
                  Average RMSE
                </div>

                <div className="text-3xl font-bold text-gray-900 mt-2">
                  {formatValue(avgRmseMetal)}
                </div>
              </div>

              <div className="bg-orange-100 text-orange-700 px-3 py-2 rounded-lg">
                RMSE
              </div>
            </div>

            <p className="text-xs text-gray-400 mt-5">
              Root Mean Squared Error
            </p>
          </div>
        </div>
      </div>

      {/* Alumina Recovery Metrics */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Alumina Recovery Model
        </h2>

        <div className="grid grid-cols-3 gap-6">

          {/* R2 */}
          <div className="bg-white rounded-2xl shadow p-6">
            <div className="flex justify-between items-start">
              <div>
                <div className="text-sm text-gray-500">
                  Average R²
                </div>

                <div className="text-3xl font-bold text-gray-900 mt-2">
                  {formatValue(avgR2Alumina)}
                </div>
              </div>

              <div className="bg-green-100 text-green-700 px-3 py-2 rounded-lg">
                R²
              </div>
            </div>

            <div className="mt-5 h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 rounded-full"
                style={{ width: getR2Width(avgR2Alumina) }}
              />
            </div>

            <p className="text-xs text-gray-400 mt-2">
              Higher is better
            </p>
          </div>

          {/* MAE */}
          <div className="bg-white rounded-2xl shadow p-6">
            <div className="flex justify-between items-start">
              <div>
                <div className="text-sm text-gray-500">
                  Average MAE
                </div>

                <div className="text-3xl font-bold text-gray-900 mt-2">
                  {formatValue(avgMaeAlumina)}
                </div>
              </div>

              <div className="bg-purple-100 text-purple-700 px-3 py-2 rounded-lg">
                MAE
              </div>
            </div>

            <p className="text-xs text-gray-400 mt-5">
              Mean Absolute Error
            </p>
          </div>

          {/* RMSE */}
          <div className="bg-white rounded-2xl shadow p-6">
            <div className="flex justify-between items-start">
              <div>
                <div className="text-sm text-gray-500">
                  Average RMSE
                </div>

                <div className="text-3xl font-bold text-gray-900 mt-2">
                  {formatValue(avgRmseAlumina)}
                </div>
              </div>

              <div className="bg-orange-100 text-orange-700 px-3 py-2 rounded-lg">
                RMSE
              </div>
            </div>

            <p className="text-xs text-gray-400 mt-5">
              Root Mean Squared Error
            </p>
          </div>
        </div>
      </div>

      {/* Analysis Performance Table */}
      <div className="bg-white rounded-2xl shadow overflow-hidden">

        <div className="p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">
            Analysis Performance History
          </h2>

          <p className="text-sm text-gray-500 mt-1">
            Model metrics recorded from completed analyses.
          </p>
        </div>

        {validRows.length === 0 ? (
          <div className="p-10 text-center">
            <div className="text-gray-500">
              No model metrics available yet.
            </div>

            <p className="text-sm text-gray-400 mt-2">
              Run an analysis to generate model performance metrics.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">

              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">
                    Model
                  </th>

                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">
                    Metal R²
                  </th>

                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">
                    Metal MAE
                  </th>

                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">
                    Metal RMSE
                  </th>

                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">
                    Alumina R²
                  </th>

                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">
                    Alumina MAE
                  </th>

                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">
                    Alumina RMSE
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-100">
                {validRows.map((row, index) => (
                  <tr
                    key={row.id ?? index}
                    className="hover:bg-gray-50"
                  >
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">
                        {row.model_used || '—'}
                      </div>

                      <div className="text-xs text-gray-400">
                        {row.model_type || ''}
                      </div>
                    </td>

                    <td className="px-6 py-4 font-medium text-green-600">
                      {formatValue(row.r2_metal)}
                    </td>

                    <td className="px-6 py-4 text-gray-700">
                      {formatValue(row.mae_metal)}
                    </td>

                    <td className="px-6 py-4 text-gray-700">
                      {formatValue(row.rmse_metal)}
                    </td>

                    <td className="px-6 py-4 font-medium text-green-600">
                      {formatValue(row.r2_alumina)}
                    </td>

                    <td className="px-6 py-4 text-gray-700">
                      {formatValue(row.mae_alumina)}
                    </td>

                    <td className="px-6 py-4 text-gray-700">
                      {formatValue(row.rmse_alumina)}
                    </td>
                  </tr>
                ))}
              </tbody>

            </table>
          </div>
        )}
      </div>

      {/* Information */}
      <div className="bg-blue-50 border border-blue-100 rounded-xl p-5">
        <h3 className="font-semibold text-blue-900">
          About these metrics
        </h3>

        <p className="text-sm text-blue-800 mt-2">
          R² indicates how well the model explains the variation in the
          recovery results. MAE and RMSE measure prediction error, where
          lower values generally indicate better prediction accuracy.
        </p>
      </div>

    </div>
  );
}