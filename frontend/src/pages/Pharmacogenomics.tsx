export default function Pharmacogenomics() {
  return (
    <div className="flex flex-col gap-6 h-full pb-10">
      <div className="flex items-center gap-2">
        <h1 className="text-3xl font-bold text-gray-900">Pharmacogenomics</h1>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-500 border border-gray-200 flex items-center gap-1 uppercase tracking-wider">
          PLANNED
        </span>
      </div>
      <p className="text-gray-500">Drug-gene interaction screening</p>

      <div className="bg-white border border-gray-200 rounded-xl shadow-sm flex flex-col flex-1 items-center justify-center p-8 text-center min-h-[400px]">
        <div className="w-16 h-16 rounded-full bg-gray-50 mb-4 flex items-center justify-center border border-gray-100">
          <span className="material-symbols-outlined text-3xl text-gray-400">medication</span>
        </div>
        <h3 className="font-medium text-gray-900 mb-2">Module Planned</h3>
        <p className="text-sm text-gray-500 max-w-md">
          This feature will provide drug response predictions based on genetic variants. It is currently planned for future development and not yet implemented.
        </p>
      </div>
    </div>
  );
}
