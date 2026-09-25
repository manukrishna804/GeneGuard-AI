export default function WESAnalysis() {
  return (
    <div className="flex flex-col gap-6 h-full pb-10">
      {/* TopAppBar */}
      <div className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-xl shadow-sm">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-primary">
            <span className="material-symbols-outlined">person</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-gray-900 leading-tight">Patient Context</h2>
              <span className="bg-amber-100 text-amber-700 border border-amber-200 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">Demo Patient</span>
            </div>
            <p className="text-sm text-gray-500">Eleanor Vance • 34y Female • DOB: 14-Oct-1989 • MRN: GG-8921-WES</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-500 hover:text-primary transition-colors">
            <span className="material-symbols-outlined text-lg">share</span>
            <span className="hidden sm:inline">Share Case</span>
          </button>
          <button className="flex items-center gap-1 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg text-sm font-medium text-primary hover:bg-gray-100 transition-colors">
            <span className="material-symbols-outlined text-lg">download</span>
            <span>Download Report</span>
          </button>
        </div>
      </div>

      {/* Header Banner */}
      <section className="bg-white border border-gray-200 rounded-xl p-6 flex flex-col lg:flex-row justify-between lg:items-center gap-4 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-gray-900">WES Analysis & Variant Curation</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1 uppercase tracking-wider">
              <div className="w-1.5 h-1.5 rounded-full bg-amber-500"></div> IN PROGRESS
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-1 flex flex-wrap items-center gap-x-2">
            <span className="font-semibold text-gray-900">Workflow:</span> Input: structured WES report (variant list) → ClinVar & gnomAD lookup → AI-generated explanation
          </p>
        </div>
        <div className="flex items-center gap-4 bg-gray-50 px-4 py-2.5 rounded-lg border border-gray-200 text-sm">
          <div>
            <span className="block text-[11px] uppercase tracking-wider text-gray-500 font-bold">Data Source</span>
            <span className="font-bold text-primary text-lg">Demo VCF</span>
          </div>
          <div className="h-8 w-px bg-gray-200"></div>
          <div>
            <span className="block text-[11px] uppercase tracking-wider text-gray-500 font-bold">Variants</span>
            <span className="font-bold text-gray-900 text-lg">24</span>
          </div>
        </div>
      </section>

      {/* Top Metrics Banner */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="bg-white border border-gray-200 rounded-xl p-5 flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Pathogenic / Likely Pathogenic</span>
            <span className="p-1.5 bg-error/10 text-error rounded-lg">
              <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>warning</span>
            </span>
          </div>
          <div className="mt-3 relative">
            <div className="flex items-baseline gap-2">
              <span className="text-3xl text-error font-bold">2</span>
              <span className="text-sm text-gray-500 font-medium">variants detected</span>
            </div>
            <div className="flex gap-1.5 mt-2">
              <span className="px-2 py-0.5 bg-error/10 text-error text-[11px] font-semibold rounded border border-error/20">BRCA1</span>
              <span className="px-2 py-0.5 bg-error/10 text-error text-[11px] font-semibold rounded border border-error/20">LDLR</span>
            </div>
            <span className="absolute bottom-0 right-0 text-[9px] uppercase tracking-widest font-bold text-gray-400 bg-gray-50 px-1.5 py-0.5 rounded border border-gray-200">Demo Data</span>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-5 flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Variants of Uncertain Sig.</span>
            <span className="p-1.5 bg-[#fef7e0] text-[#b06000] rounded-lg">
              <span className="material-symbols-outlined text-lg">help</span>
            </span>
          </div>
          <div className="mt-3 relative">
            <div className="flex items-baseline gap-2">
              <span className="text-3xl text-[#b06000] font-bold">4</span>
              <span className="text-sm text-gray-500 font-medium">under curation</span>
            </div>
            <div className="flex gap-1.5 mt-2">
              <span className="px-2 py-0.5 bg-[#fef7e0] text-[#b06000] text-[11px] font-semibold rounded border border-[#fce8b2]">MSH2</span>
              <span className="px-2 py-0.5 bg-[#fef7e0] text-[#b06000] text-[11px] font-semibold rounded border border-[#fce8b2]">KCNQ1</span>
              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-[11px] font-semibold rounded border border-gray-200">+2 more</span>
            </div>
            <span className="absolute bottom-0 right-0 text-[9px] uppercase tracking-widest font-bold text-gray-400 bg-gray-50 px-1.5 py-0.5 rounded border border-gray-200">Demo Data</span>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-5 flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Benign / Likely Benign</span>
            <span className="p-1.5 bg-[#e6f4ea] text-[#137333] rounded-lg">
              <span className="material-symbols-outlined text-lg">check_circle</span>
            </span>
          </div>
          <div className="mt-3 relative">
            <div className="flex items-baseline gap-2">
              <span className="text-3xl text-[#137333] font-bold">18</span>
              <span className="text-sm text-gray-500 font-medium">annotated</span>
            </div>
            <p className="text-xs text-gray-500 mt-2">High gnomAD AF (&gt;1%) concordant with ACMG BA1</p>
            <span className="absolute bottom-0 right-0 text-[9px] uppercase tracking-widest font-bold text-gray-400 bg-gray-50 px-1.5 py-0.5 rounded border border-gray-200">Demo Data</span>
          </div>
        </div>
      </section>

      {/* Variant Table Placeholder */}
      <section className="bg-white border border-gray-200 rounded-xl flex flex-col overflow-hidden min-h-[400px] shadow-sm">
        <div className="p-5 border-b border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gray-50/50">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <span className="material-symbols-outlined text-gray-500">list_alt</span>
            Prioritized Variants
          </h3>
          <span className="text-[10px] uppercase tracking-widest font-bold text-amber-700 bg-amber-50 px-2 py-1 rounded border border-amber-200">
            Integration Pending
          </span>
        </div>
        <div className="p-6 flex-1 flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 rounded-full bg-gray-50 mb-4 flex items-center justify-center border border-gray-100">
            <span className="material-symbols-outlined text-3xl text-gray-400">table_chart</span>
          </div>
          <h3 className="font-medium text-gray-900 mb-1">Variant Browser Backend Pending</h3>
          <p className="text-sm text-gray-500 max-w-md">
            The FastAPI endpoint for ClinVar/gnomAD variant lookup is built, but PDF parsing and frontend table integration is currently in progress.
          </p>
        </div>
      </section>
    </div>
  );
}
