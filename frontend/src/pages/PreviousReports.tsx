import React, { useEffect, useState } from 'react';
import { reports } from '../api/endpoints';

interface Report {
  id: number;
  sample_id?: string;
  test_method?: string;
  filename?: string;
  filepath?: string;
  created_at?: string;
  created_date?: string;
}

export default function PreviousReports() {
  const [list, setList] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<number | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      setError('');

      const res = await reports.history();
      setList(res.data || []);
    } catch (err) {
      console.error(err);
      setError('Unable to load previous reports.');
    } finally {
      setLoading(false);
    }
  };

  const download = async (report: Report) => {
    try {
      setDownloading(report.id);

      const res = await reports.download(report.id);

      const blob = new Blob([res.data], {
        type: 'application/pdf',
      });

      const url = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;

      const filename =
        report.filename ||
        `ReAlux_Report_${report.sample_id || report.id}.pdf`;

      link.setAttribute('download', filename);

      document.body.appendChild(link);
      link.click();

      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert('Report download failed. Please try again.');
    } finally {
      setDownloading(null);
    }
  };

  const formatDate = (date?: string) => {
    if (!date) return 'Date unavailable';

    const parsed = new Date(date);

    if (isNaN(parsed.getTime())) {
      return date;
    }

    return parsed.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <div className="space-y-8">

      {/* Header */}
      <div className="flex items-center justify-between">

        <div>
          <div className="text-sm font-semibold text-blue-600 mb-1">
            ReAlux Reports
          </div>

          <h1 className="text-3xl font-bold text-gray-900">
            Previous Reports
          </h1>

          <p className="text-gray-500 mt-2">
            View and download your previously generated analysis reports.
          </p>
        </div>

        <div className="bg-blue-50 px-5 py-3 rounded-xl text-center">
          <div className="text-sm text-blue-600">
            Total Reports
          </div>

          <div className="text-2xl font-bold text-blue-800">
            {list.length}
          </div>
        </div>

      </div>

      {/* Loading */}
      {loading && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-12 text-center">

          <div className="animate-spin h-10 w-10 border-4 border-blue-200 border-t-blue-600 rounded-full mx-auto mb-4"></div>

          <p className="text-gray-500">
            Loading previous reports...
          </p>

        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-5 text-red-700">
          <div className="font-semibold mb-1">
            Unable to load reports
          </div>

          <div className="text-sm">
            {error}
          </div>

          <button
            onClick={loadReports}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Empty */}
      {!loading && !error && list.length === 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-12 text-center">

          <div className="text-6xl mb-5">
            📄
          </div>

          <h2 className="text-xl font-bold text-gray-800">
            No reports yet
          </h2>

          <p className="text-gray-500 mt-2 max-w-md mx-auto">
            Once you complete an analysis and generate a PDF report,
            it will appear here.
          </p>

        </div>
      )}

      {/* Reports */}
      {!loading && !error && list.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">

          {/* Table Header */}
          <div className="px-6 py-5 border-b border-gray-200 flex items-center justify-between">

            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Generated Reports
              </h2>

              <p className="text-sm text-gray-500 mt-1">
                {list.length} report{list.length !== 1 ? 's' : ''} available
              </p>
            </div>

            <button
              onClick={loadReports}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
            >
              ↻ Refresh
            </button>

          </div>

          {/* Desktop Table */}
          <div className="overflow-x-auto">

            <table className="min-w-full">

              <thead className="bg-gray-50">

                <tr>

                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                    Report
                  </th>

                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                    Sample
                  </th>

                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                    Method
                  </th>

                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                    Date
                  </th>

                  <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wide">
                    Action
                  </th>

                </tr>

              </thead>

              <tbody className="divide-y divide-gray-100">

                {list.map((report, index) => (

                  <tr
                    key={report.id}
                    className="hover:bg-gray-50 transition"
                  >

                    {/* Report */}
                    <td className="px-6 py-5">

                      <div className="flex items-center gap-3">

                        <div className="w-11 h-11 rounded-xl bg-red-50 flex items-center justify-center text-xl">
                          📄
                        </div>

                        <div>

                          <div className="font-semibold text-gray-900">
                            ReAlux Report #{report.id}
                          </div>

                          <div className="text-xs text-gray-400 mt-1">
                            PDF Document
                          </div>

                        </div>

                      </div>

                    </td>

                    {/* Sample */}
                    <td className="px-6 py-5">

                      <div className="font-medium text-gray-800">
                        {report.sample_id || 'Unknown Sample'}
                      </div>

                    </td>

                    {/* Method */}
                    <td className="px-6 py-5">

                      <div className="text-gray-700 max-w-xs">
                        {report.test_method || 'Analysis Report'}
                      </div>

                    </td>

                    {/* Date */}
                    <td className="px-6 py-5">

                      <div className="text-gray-700">
                        {formatDate(
                          report.created_at || report.created_date
                        )}
                      </div>

                    </td>

                    {/* Download */}
                    <td className="px-6 py-5 text-right">

                      <button
                        onClick={() => download(report)}
                        disabled={downloading === report.id}
                        className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition ${
                          downloading === report.id
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                      >

                        {downloading === report.id ? (
                          <>
                            <span className="animate-spin">
                              ⟳
                            </span>

                            Downloading...
                          </>
                        ) : (
                          <>
                            ↓
                            Download PDF
                          </>
                        )}

                      </button>

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        </div>
      )}

      {/* Information */}
      {!loading && list.length > 0 && (
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-5">

          <div className="flex gap-3">

            <div className="text-xl">
              ℹ️
            </div>

            <div>

              <h3 className="font-semibold text-blue-900">
                About your reports
              </h3>

              <p className="text-sm text-blue-700 mt-1">
                Reports are generated from your completed aluminium dross
                recovery analyses. Click "Download PDF" to save a report
                to your computer.
              </p>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}