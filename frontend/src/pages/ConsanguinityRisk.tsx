import { useState } from 'react';

export default function ConsanguinityRisk() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const assessRisk = async () => {
    setLoading(true);
    try {
      const response = await fetch('/consanguinity/assess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ /* payload */ })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 h-full pb-10">
      <div className="flex items-center gap-2">
        <h1 className="text-3xl font-bold text-gray-900">Consanguinity Risk</h1>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-green-50 text-green-700 border border-green-200 flex items-center gap-1 uppercase tracking-wider">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div> READY
        </span>
      </div>
      <p className="text-gray-500">Punnett-square based offspring risk calculator</p>

      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 text-gray-900 flex items-center gap-2">
          <span className="material-symbols-outlined text-primary">person_add</span>
          Patient Inputs
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
          <div className="flex flex-col gap-2">
            <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Patient ID</label>
            <input type="text" className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none text-gray-900" placeholder="e.g. GG-8921" />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Consanguinity Degree</label>
            <select className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none text-gray-900">
              <option value="first_cousins">First Cousins</option>
              <option value="second_cousins">Second Cousins</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        <button 
          onClick={assessRisk}
          disabled={loading}
          className="mt-6 bg-primary hover:bg-[#005049] text-white font-medium text-sm px-6 py-2.5 rounded-lg flex items-center justify-center gap-2 shadow-sm transition-colors disabled:opacity-50"
        >
          {loading ? 'Calculating...' : 'Calculate Risk'}
        </button>

        {result && (
          <div className="mt-8 p-5 bg-gray-50 border border-gray-200 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary">check_circle</span>
              Assessment Results
            </h3>
            <pre className="bg-white border border-gray-200 rounded-lg p-4 text-sm text-gray-700 overflow-x-auto font-mono shadow-sm">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
