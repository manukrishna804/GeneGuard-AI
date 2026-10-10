import { useState } from 'react';

export default function FamilyPedigree() {
  const [patientId, setPatientId] = useState('GG-8921');
  const [treeData, setTreeData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchTree = async () => {
    if (!patientId) return;
    setLoading(true);
    try {
      const response = await fetch(`/family-history/patient/${patientId}/tree`);
      const data = await response.json();
      setTreeData(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeHistory = async () => {
    if (!patientId) return;
    setLoading(true);
    try {
      const response = await fetch(`/family-history/patient/${patientId}/analyze`, {
        method: 'POST'
      });
      const data = await response.json();
      console.log('Analysis:', data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 h-full pb-10">
      <div className="flex items-center gap-2">
        <h1 className="text-3xl font-bold text-gray-900">Family Pedigree</h1>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-green-50 text-green-700 border border-green-200 flex items-center gap-1 uppercase tracking-wider">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div> READY
        </span>
      </div>
      <p className="text-gray-500">Pedigree builder & inheritance pattern detection</p>

      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4 flex-1">
          <div className="flex flex-col gap-1 w-full max-w-sm">
            <label className="text-[11px] font-bold text-gray-500 uppercase tracking-wider">Patient ID</label>
            <input 
              type="text" 
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none text-gray-900" 
              placeholder="e.g. GG-8921" 
            />
          </div>
        </div>
        <div className="flex gap-2 sm:mt-5">
          <button 
            onClick={fetchTree}
            className="bg-gray-50 hover:bg-gray-100 text-primary font-medium text-sm px-4 py-2 rounded-lg border border-gray-200 transition-colors flex items-center gap-2 shadow-sm"
          >
            <span className="material-symbols-outlined text-lg">account_tree</span>
            Load Tree
          </button>
          <button 
            onClick={analyzeHistory}
            className="bg-primary hover:bg-[#005049] text-white font-medium text-sm px-4 py-2 rounded-lg transition-colors flex items-center gap-2 shadow-sm"
          >
            <span className="material-symbols-outlined text-lg">analytics</span>
            Analyze History
          </button>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm min-h-[500px] flex items-center justify-center">
        {loading ? (
          <div className="text-gray-500 flex flex-col items-center gap-2">
            <span className="material-symbols-outlined animate-spin text-2xl text-primary">autorenew</span>
            <span>Loading pedigree data...</span>
          </div>
        ) : treeData ? (
          <pre className="text-left w-full h-full bg-gray-50 p-4 rounded-lg text-sm font-mono border border-gray-200 overflow-auto">
            {JSON.stringify(treeData, null, 2)}
          </pre>
        ) : (
          <div className="text-gray-400 flex flex-col items-center">
            <span className="material-symbols-outlined text-4xl mb-2 opacity-50">account_tree</span>
            <p>Enter a patient ID and load tree data</p>
          </div>
        )}
      </div>
    </div>
  );
}
