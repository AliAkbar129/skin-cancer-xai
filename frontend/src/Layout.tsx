import React from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { Activity, LayoutDashboard, ScanSearch, Network, Users, Settings, Bell, Search, UserCircle } from 'lucide-react';
import { cn } from './utils/cn';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/analysis', label: 'New Analysis', icon: ScanSearch },
  { path: '/patients', label: 'Patient Records', icon: Users },
  { path: '/architecture', label: 'Model Architecture', icon: Network },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export function Layout() {
  const location = useLocation();

  return (
    <div className="flex h-screen bg-[#050508] text-gray-100 overflow-hidden font-sans selection:bg-purple-500/30">
      {/* Background glow for the entire app */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-900/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-900/10 blur-[120px] pointer-events-none" />

      {/* Sidebar */}
      <aside className="w-64 border-r border-white/5 bg-black/40 backdrop-blur-xl flex flex-col z-10 relative">
        <div className="h-20 flex items-center px-6 border-b border-white/5">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg shadow-[0_0_15px_rgba(59,130,246,0.5)]">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div className="ml-3">
            <h1 className="text-lg font-bold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-gray-100 to-gray-400">
              DERMO<span className="text-blue-400">XAI</span>
            </h1>
          </div>
        </div>

        <nav className="flex-1 py-6 px-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={cn(
                  "flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 group",
                  isActive 
                    ? "bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 text-blue-400 shadow-[inset_0_0_20px_rgba(59,130,246,0.05)]" 
                    : "text-gray-400 hover:text-gray-100 hover:bg-white/5"
                )}
              >
                <Icon className={cn("w-5 h-5 transition-colors", isActive ? "text-blue-400" : "group-hover:text-gray-200")} />
                <span className="font-medium text-sm">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="p-4 border-t border-white/5">
          <div className="flex items-center space-x-3 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
            <UserCircle className="w-8 h-8 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-200">Dr. Sarah Jenkins</p>
              <p className="text-xs text-gray-500">Lead Dermatologist</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-screen relative z-10">
        {/* Top Header */}
        <header className="h-20 border-b border-white/5 bg-black/20 backdrop-blur-md flex items-center justify-between px-8">
          <div className="relative w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input 
              type="text" 
              placeholder="Search patients, scans, or reports..." 
              className="w-full bg-white/5 border border-white/10 rounded-full py-2 pl-10 pr-4 text-sm text-gray-200 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all placeholder:text-gray-600"
            />
          </div>
          <div className="flex items-center space-x-4">
            <button className="relative p-2 rounded-full hover:bg-white/10 transition-colors text-gray-400 hover:text-gray-200">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-purple-500 rounded-full border border-[#050508]"></span>
            </button>
            <div className="h-6 w-px bg-white/10 mx-2"></div>
            <span className="text-sm font-medium text-gray-400">
              {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'long', day: 'numeric' })}
            </span>
          </div>
        </header>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
