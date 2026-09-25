export default function ComplexDiseaseRisk() {
  return (
    <div className="flex flex-col gap-6 h-full pb-10">
      <div className="flex items-center gap-2">
        <h1 className="text-3xl font-bold text-gray-900">Complex Disease Risk</h1>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1 uppercase tracking-wider">
          <div className="w-1.5 h-1.5 rounded-full bg-amber-500"></div> IN PROGRESS
        </span>
      </div>
      <p className="text-gray-500">ML-based risk scoring (diabetes, heart disease)</p>

      <div className="bg-white border border-gray-200 rounded-xl shadow-sm flex flex-col flex-1 items-center justify-center p-8 text-center min-h-[400px]">
        <div className="w-16 h-16 rounded-full bg-gray-50 mb-4 flex items-center justify-center border border-gray-100">
          <span className="material-symbols-outlined text-3xl text-amber-500">model_training</span>
        </div>
        <h3 className="font-medium text-gray-900 mb-2">API Integration Pending</h3>
        <p className="text-sm text-gray-500 max-w-md">
          The ML models for blood biomarker and lifestyle factor classification have been trained, but frontend API integration is pending.
        </p>
      </div>
    </div>
  );
}
