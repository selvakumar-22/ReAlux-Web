import React, { useEffect, useState } from 'react';
import { dataset } from '../api/endpoints';

export default function Dataset() {
  const [data, setData] = useState<any>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadDataset();
  }, []);

  const loadDataset = async () => {
    try {
      const res = await dataset.get();
      setData(res.data);
    } catch (err) {
      console.error('Failed to load dataset:', err);
    }
  };

  const handleUpload = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];

    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.csv')) {
      alert('Please upload a CSV file.');
      return;
    }

    try {
      setUploading(true);

      await dataset.upload(file);

      alert('Dataset uploaded successfully');

      await loadDataset();
    } catch (err) {
      console.error(err);
      alert('Dataset upload failed');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  if (!data) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500">Loading dataset...</p>
        </div>
      </div>
    );
  }

  const stats = data.stats || {};
  const columns = data.columns || [];
  const rows = data.rows || [];

  return (
    <div className="space-y-8">

      {/* HEADER */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">

        <div>
          <div className="text-sm font-semibold text-blue-600 mb-1">
            ReAlux Data Management
          </div>

          <h1 className="text-3xl font-bold text-gray-900">
            Dataset
          </h1>

          <p className="text-gray-500 mt-2">
            View, inspect and upload aluminium dross analysis datasets.
          </p>
        </div>

        {/* Upload Button */}
        <label
          className={`inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl font-semibold cursor-pointer transition ${
            uploading
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 shadow-md'
          }`}
        >
          <span className="text-lg">
            {uploading ? '⏳' : '↑'}
          </span>

          {uploading ? 'Uploading...' : 'Upload CSV'}

          <input
            type="file"
            accept=".csv"
            onChange={handleUpload}
            disabled={uploading}
            className="hidden"
          />
        </label>

      </div>

      {/* DATASET STATS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">

        {/* Samples */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">

            <div>
              <p className="text-sm text-gray-500">
                Total Samples
              </p>

              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats.num_samples ?? 0}
              </p>

              <p className="text-xs text-gray-400 mt-2">
                Dataset records
              </p>
            </div>

            <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center text-2xl">
              📊
            </div>

          </div>
        </div>

        {/* Features */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">

            <div>
              <p className="text-sm text-gray-500">
                Features
              </p>

              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats.num_features ?? 0}
              </p>

              <p className="text-xs text-gray-400 mt-2">
                Available columns
              </p>
            </div>

            <div className="w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center text-2xl">
              🧪
            </div>

          </div>
        </div>

        {/* Missing Values */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">

            <div>
              <p className="text-sm text-gray-500">
                Missing Values
              </p>

              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats.missing_values ?? 0}
              </p>

              <p className="text-xs text-gray-400 mt-2">
                Empty data cells
              </p>
            </div>

            <div className="w-12 h-12 rounded-xl bg-orange-50 flex items-center justify-center text-2xl">
              ⚠️
            </div>

          </div>
        </div>

        {/* Duplicate Rows */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">

            <div>
              <p className="text-sm text-gray-500">
                Duplicate Rows
              </p>

              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats.duplicate_rows ?? 0}
              </p>

              <p className="text-xs text-gray-400 mt-2">
                Repeated records
              </p>
            </div>

            <div className="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center text-2xl">
              ✓
            </div>

          </div>
        </div>

      </div>

      {/* DATASET OVERVIEW */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">

          <div>
            <h2 className="text-xl font-bold text-gray-900">
              Dataset Overview
            </h2>

            <p className="text-sm text-gray-500 mt-1">
              Preview of the uploaded dataset.
            </p>
          </div>

          <div className="text-sm text-gray-500">
            Showing{' '}
            <span className="font-semibold text-gray-900">
              {rows.length}
            </span>{' '}
            records
          </div>

        </div>

        {/* TABLE */}
        <div className="overflow-x-auto rounded-xl border border-gray-200">

          {columns.length > 0 ? (
            <table className="min-w-full text-sm">

              <thead className="bg-gray-50">
                <tr>
                  {columns.map((col: string) => (
                    <th
                      key={col}
                      className="px-5 py-4 text-left font-semibold text-gray-700 border-b whitespace-nowrap"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-100">

                {rows.length > 0 ? (
                  rows.map((row: any, idx: number) => (
                    <tr
                      key={idx}
                      className="hover:bg-gray-50 transition"
                    >

                      {columns.map((col: string) => (
                        <td
                          key={col}
                          className="px-5 py-4 text-gray-600 whitespace-nowrap"
                        >
                          {row[col] !== null &&
                          row[col] !== undefined &&
                          row[col] !== ''
                            ? String(row[col])
                            : (
                              <span className="text-gray-300">
                                —
                              </span>
                            )}
                        </td>
                      ))}

                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan={columns.length}
                      className="px-5 py-12 text-center text-gray-400"
                    >
                      No dataset records available.
                    </td>
                  </tr>
                )}

              </tbody>

            </table>
          ) : (
            <div className="py-12 text-center text-gray-400">
              No dataset columns available.
            </div>
          )}

        </div>

      </div>

      {/* UPLOAD INFORMATION */}
      <div className="bg-blue-50 border border-blue-100 rounded-2xl p-6">

        <div className="flex gap-4">

          <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center text-xl shrink-0">
            ℹ️
          </div>

          <div>
            <h3 className="font-semibold text-gray-900">
              Dataset Upload
            </h3>

            <p className="text-sm text-gray-600 mt-1">
              Upload a CSV file containing aluminium dross
              composition and recovery data. The uploaded dataset
              will be used by the analysis and machine learning
              workflow.
            </p>

            <p className="text-xs text-gray-500 mt-3">
              Supported format: <strong>.csv</strong>
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}