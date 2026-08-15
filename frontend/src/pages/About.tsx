export default function About() {
  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="text-blue-600 font-semibold mb-2">
          ReAlux Decision Support System
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          About ReAlux
        </h1>

        <p className="text-gray-600 text-lg max-w-3xl">
          ReAlux is an AI-powered decision support system designed to analyse
          aluminium dross composition, estimate recovery performance, evaluate
          risk, and support recycling process decisions.
        </p>
      </div>

      {/* Main Purpose */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-3">
          What is ReAlux?
        </h2>

        <p className="text-gray-600 leading-7">
          ReAlux helps users analyse aluminium dross data and understand the
          potential recovery of valuable materials. The system combines
          composition data, analytical models, recovery estimates, and
          decision-support information in a single platform.
        </p>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="text-3xl mb-4">📊</div>

          <h2 className="text-lg font-bold text-gray-900 mb-2">
            Analysis & Recovery
          </h2>

          <p className="text-gray-600 leading-6">
            Analyse aluminium dross composition and estimate metal and alumina
            recovery performance from available analysis data.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="text-3xl mb-4">🤖</div>

          <h2 className="text-lg font-bold text-gray-900 mb-2">
            AI-Based Decision Support
          </h2>

          <p className="text-gray-600 leading-6">
            Use analytical models and model results to support recovery method
            selection and process-related decisions.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="text-3xl mb-4">🛡️</div>

          <h2 className="text-lg font-bold text-gray-900 mb-2">
            Risk Evaluation
          </h2>

          <p className="text-gray-600 leading-6">
            Review risk-level information and safety guidance associated with
            the analysed material.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="text-3xl mb-4">📄</div>

          <h2 className="text-lg font-bold text-gray-900 mb-2">
            Professional Reports
          </h2>

          <p className="text-gray-600 leading-6">
            Generate PDF reports containing analysis results, recovery
            information, model details, and safety-related information.
          </p>
        </div>
      </div>

      {/* Workflow */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">
          How ReAlux Works
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div>
            <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold mb-3">
              1
            </div>

            <h3 className="font-semibold text-gray-900 mb-1">
              Input Data
            </h3>

            <p className="text-sm text-gray-600">
              Provide aluminium dross composition and analysis information.
            </p>
          </div>

          <div>
            <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold mb-3">
              2
            </div>

            <h3 className="font-semibold text-gray-900 mb-1">
              Analyse
            </h3>

            <p className="text-sm text-gray-600">
              The system processes the available data using its analysis
              workflow.
            </p>
          </div>

          <div>
            <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold mb-3">
              3
            </div>

            <h3 className="font-semibold text-gray-900 mb-1">
              Evaluate
            </h3>

            <p className="text-sm text-gray-600">
              Review recovery estimates, recommended methods, model results,
              and risk information.
            </p>
          </div>

          <div>
            <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold mb-3">
              4
            </div>

            <h3 className="font-semibold text-gray-900 mb-1">
              Report
            </h3>

            <p className="text-sm text-gray-600">
              Generate and download a PDF report for the completed analysis.
            </p>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-blue-50 border border-blue-100 rounded-xl p-5">
        <h2 className="font-bold text-gray-900 mb-2">
          Important Note
        </h2>

        <p className="text-sm text-gray-600 leading-6">
          ReAlux is a decision-support application. Analysis results should be
          interpreted together with verified laboratory measurements, process
          requirements, safety data, and appropriate professional judgement.
        </p>
      </div>
    </div>
  );
}