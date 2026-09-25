import { Outlet, NavLink } from 'react-router-dom';

export default function Layout() {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: 'dashboard' },
    { name: 'Genetic Disorder ID', path: '/wes-analysis', icon: 'biotech' },
    { name: 'Facial Phenotype', path: '/facial-phenotype', icon: 'person_search' },
    { name: 'Complex Disease Risk', path: '/complex-disease', icon: 'ecg_heart' },
    { name: 'Consanguinity Risk', path: '/consanguinity', icon: 'family_history' },
    { name: 'Pharmacogenomics', path: '/pharmacogenomics', icon: 'medication' },
    { name: 'Family Pedigree', path: '/pedigree', icon: 'account_tree' },
  ];

  return (
    <div className="bg-[#f8f9fa] text-gray-900 font-sans antialiased min-h-screen flex flex-col">
      {/* Top Header */}
      <header className="fixed top-0 w-full z-50 flex items-center justify-between px-6 h-16 bg-white border-b border-gray-200">
        <div className="flex items-center gap-8 w-1/3">
          <div className="flex items-center gap-2 cursor-pointer">
            <span className="material-symbols-outlined text-primary text-3xl font-bold">science</span>
            <span className="text-xl font-bold text-primary tracking-tight">GeneGuard AI</span>
          </div>
        </div>
        
        <div className="w-1/3 flex justify-center">
          <div className="relative w-full max-w-md">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-400">
              <span className="material-symbols-outlined text-xl">search</span>
            </span>
            <input 
              className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-gray-900 placeholder-gray-500" 
              placeholder="Search patients, variants, or reports..." 
              type="text" 
            />
          </div>
        </div>

        <div className="flex items-center justify-end gap-4 w-1/3">
          <button className="text-gray-500 hover:text-gray-700 transition-colors cursor-pointer relative" title="Notifications">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <button className="text-gray-500 hover:text-gray-700 transition-colors cursor-pointer" title="Settings">
            <span className="material-symbols-outlined">settings</span>
          </button>
          <button className="bg-primary hover:bg-[#005049] text-white font-medium text-sm px-4 py-2 rounded-lg shadow-sm transition-colors cursor-pointer">
            Run Analysis
          </button>
          <img 
            alt="Profile" 
            className="w-8 h-8 rounded-full object-cover border border-gray-200" 
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuB7035javUZlrqbmoCXTbG3Ig8nVXGz5sTv9HG8J3W4ylngtHLu-_M_vzcpKnLdFp8oczNccx3yl0lmtiKaA5tqzoJ0kYzmDnZwMpETl6rmsa-_aGWqcf1etyLngyZMUUMPCYYZ-pReE0gCbAfEtGedVe014MKOSmJ1VhfvKRosFBdz0l4Mhbw9LtEvSxVdC7M-QXFIVNmZYYvqdVBDDFWIcbCQKwnlF-da6xBCsnbDvTLJ7azit3pK" 
          />
        </div>
      </header>

      {/* Sidebar */}
      <aside className="fixed left-0 top-16 h-[calc(100vh-64px)] w-64 flex flex-col p-4 bg-white border-r border-gray-200 z-40 overflow-y-auto">
        <div className="pb-4 mb-2">
          <div className="flex items-center gap-2 mb-1 text-primary">
            <span className="material-symbols-outlined">hub</span>
            <span className="font-semibold tracking-tight">Clinical Modules</span>
          </div>
          <p className="text-[11px] text-gray-500 uppercase tracking-wider font-semibold">Diagnostic Suite</p>
        </div>
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                isActive
                  ? "flex items-center gap-3 px-3 py-2.5 bg-gray-50 text-primary font-semibold rounded-lg transition-all"
                  : "flex items-center gap-3 px-3 py-2.5 text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-lg transition-all"
              }
            >
              <span className="material-symbols-outlined text-xl">{item.icon}</span>
              <span className="text-sm">{item.name}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="ml-64 mt-16 p-6 flex-1 bg-[#f8f9fa] min-h-[calc(100vh-64px)] flex flex-col gap-6">
        {/* Persistent Disclaimer Banner */}
        <div className="bg-[#fef7e0] border border-[#fce8b2] text-[#b06000] px-4 py-2 rounded-lg flex items-center justify-center gap-2 text-xs font-medium shadow-sm">
          <span className="material-symbols-outlined text-base">info</span>
          Decision-support prototype — not for clinical diagnostic use. B.Tech academic project.
        </div>
        
        <Outlet />
      </main>
    </div>
  );
}
