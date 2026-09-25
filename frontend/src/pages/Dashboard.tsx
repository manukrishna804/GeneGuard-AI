import { Link } from 'react-router-dom';

export default function Dashboard() {
  const modules = [
    { name: 'Genetic Disorder ID', path: '/wes-analysis', icon: 'biotech', status: 'IN PROGRESS', desc: 'WES report parsing & ClinVar/gnomAD variant lookup' },
    { name: 'Facial Phenotype', path: '/facial-phenotype', icon: 'person_search', status: 'PLANNED', desc: 'Rule-based facial landmark screening' },
    { name: 'Complex Disease Risk', path: '/complex-disease', icon: 'ecg_heart', status: 'IN PROGRESS', desc: 'ML-based risk scoring (diabetes, heart disease)' },
    { name: 'Consanguinity Risk', path: '/consanguinity', icon: 'family_history', status: 'READY', desc: 'Punnett-square based offspring risk calculator' },
    { name: 'Pharmacogenomics', path: '/pharmacogenomics', icon: 'medication', status: 'PLANNED', desc: 'Drug-gene interaction screening' },
    { name: 'Family Pedigree', path: '/pedigree', icon: 'account_tree', status: 'READY', desc: 'Pedigree builder & inheritance pattern detection' },
  ];

  const getStatusStyle = (status: string) => {
    switch(status) {
      case 'READY':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'IN PROGRESS':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'PLANNED':
      default:
        return 'bg-gray-100 text-gray-500 border-gray-200';
    }
  };

  return (
    <div className="flex flex-col gap-6 h-full pb-10">
      {/* Welcome Header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Good Morning, Dr. Chen</h1>
          <p className="text-gray-500 mt-1">Here is your clinical overview for today, October 24, 2023.</p>
        </div>
        <div className="text-right">
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wider">Pending Reviews</p>
          <p className="text-xl font-bold text-primary">0 Reports</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 flex flex-col gap-6">
          {/* Patient Overview Summary */}
          <section className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">group</span>
                Patient Overview
              </h2>
              <button className="text-sm font-medium text-primary flex items-center gap-1 hover:underline">
                View All Patients <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-[#f8f9fa] border border-gray-100 rounded-lg p-4 flex flex-col">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Active Cases</span>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-gray-900">0</span>
                  <span className="text-xs text-gray-500">(Demo)</span>
                </div>
              </div>
              <div className="bg-[#f8f9fa] border border-gray-100 rounded-lg p-4 flex flex-col">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">High Risk Flagged</span>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-error">0</span>
                  <span className="text-xs bg-error/10 text-error px-1.5 py-0.5 rounded font-medium">Demo</span>
                </div>
              </div>
              <div className="bg-[#f8f9fa] border border-gray-100 rounded-lg p-4 flex flex-col">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Analyses Completed</span>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-gray-900">0</span>
                  <span className="text-xs text-gray-500">This Week</span>
                </div>
              </div>
            </div>
          </section>

          {/* Module Status Grid */}
          <section className="flex flex-col gap-4">
            <h2 className="text-lg font-semibold text-gray-900">Diagnostic Modules</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {modules.map(mod => (
                <Link to={mod.path} key={mod.path} className="bg-white border border-gray-200 hover:border-primary rounded-xl p-5 shadow-sm transition-all hover:shadow flex flex-col h-full">
                  <div className="flex justify-between items-start mb-4">
                    <div className="w-10 h-10 rounded-lg bg-[#eaf1ff] text-primary flex items-center justify-center">
                      <span className="material-symbols-outlined">{mod.icon}</span>
                    </div>
                    <span className={`px-2 py-0.5 border rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 ${getStatusStyle(mod.status)}`}>
                      <div className={`w-1.5 h-1.5 rounded-full ${mod.status === 'READY' ? 'bg-green-500' : mod.status === 'IN PROGRESS' ? 'bg-amber-500' : 'bg-gray-400'}`}></div>
                      {mod.status}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">{mod.name}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed mt-auto">{mod.desc}</p>
                </Link>
              ))}
            </div>
          </section>
        </div>

        {/* Recent Activity Feed */}
        <section className="flex flex-col gap-6">
          <div className="bg-white border border-gray-200 rounded-xl shadow-sm flex flex-col h-full">
            <div className="p-5 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <span className="material-symbols-outlined text-gray-500">history</span>
                Recent Activity
              </h2>
              <span className="material-symbols-outlined text-gray-400 cursor-pointer">filter_list</span>
            </div>
            
            <div className="flex flex-col flex-1 items-center justify-center p-8 text-center min-h-[300px]">
              <div className="w-16 h-16 rounded-full bg-gray-50 mb-4 flex items-center justify-center border border-gray-100">
                <span className="material-symbols-outlined text-3xl text-gray-400">inbox</span>
              </div>
              <h3 className="font-medium text-gray-900 mb-1">No recent activity yet</h3>
              <p className="text-sm text-gray-500">
                Patient data and analysis results will appear here once processed.
              </p>
              <p className="text-[10px] uppercase tracking-widest text-gray-400 mt-4 font-semibold border border-gray-200 rounded px-2 py-1 bg-gray-50">
                Demo Environment
              </p>
            </div>
            
            <div className="mt-auto p-3 text-center border-t border-gray-200 bg-gray-50 text-primary text-sm font-medium hover:bg-gray-100 cursor-pointer transition-colors rounded-b-xl">
              View Complete Log
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
