import React from 'react';
import { 
  FileCheck2, 
  LayoutDashboard, 
  FolderGit2, 
  History, 
  FlaskConical, 
  Settings as SettingsIcon,
  Cpu
} from 'lucide-react';
import { SystemHealth } from '../types';
import { TruthWisp } from './TruthWisp';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  health: SystemHealth | null;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, health }) => {
  const navItems = [
    { id: 'verify', label: 'Verify', icon: FileCheck2 },
    { id: 'dashboard', label: 'Overview', icon: LayoutDashboard },
    { id: 'documents', label: 'Documents', icon: FolderGit2 },
    { id: 'history', label: 'History', icon: History },
    { id: 'evaluation', label: 'Evaluation Lab', icon: FlaskConical },
  ];

  const isOllamaOnline = health?.ollama.status === 'online';

  return (
    <header className="border-b border-white/[0.06] bg-[#080910]/95 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-14">
          {/* Identity with Truth Wisp Miniature */}
          <div 
            className="flex items-center gap-2.5 cursor-pointer group select-none" 
            onClick={() => setActiveTab('verify')}
            title="TruthGuard — See beyond the answer"
          >
            <div className="w-8 h-8 rounded-lg bg-[#11131B] border border-white/[0.08] flex items-center justify-center overflow-hidden group-hover:border-violet-500/40 transition-colors">
              <TruthWisp size="sm" subtle state="idle" />
            </div>

            <div className="flex items-baseline gap-2">
              <span className="text-sm font-semibold tracking-tight text-[#F4F4FA] group-hover:text-violet-200 transition-colors">
                TruthGuard
              </span>
              <span className="text-xs text-[#A2A6B8] hidden sm:inline font-normal">
                See beyond the answer.
              </span>
            </div>
          </div>

          {/* Slim, Unobtrusive Navigation Segmented Control */}
          <nav className="hidden md:flex items-center gap-1 bg-[#11131B] p-1 rounded-xl border border-white/[0.06]">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-[#171A25] text-[#F4F4FA] shadow-sm border border-white/[0.08]'
                      : 'text-[#A2A6B8] hover:text-[#F4F4FA] hover:bg-white/[0.02]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-violet-400' : 'text-slate-500'}`} />
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Status & Settings Utility */}
          <div className="flex items-center gap-3">
            {/* Minimal Ollama Dot */}
            <div 
              className="flex items-center gap-1.5 text-xs text-[#A2A6B8]"
              title={`Ollama: ${isOllamaOnline ? 'Online' : 'Offline'}`}
            >
              <span className={`w-2 h-2 rounded-full ${isOllamaOnline ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]' : 'bg-rose-500'}`} />
              <span className="text-[11px] hidden sm:inline text-slate-400 font-mono">
                {isOllamaOnline ? 'Ollama' : 'Offline'}
              </span>
            </div>

            {/* Hardware Pill */}
            <div className="hidden sm:flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#11131B] border border-white/[0.06] text-[11px] text-slate-400">
              <Cpu className="w-3 h-3 text-blue-400" />
              <span>{health?.hardware.device_name ? health.hardware.device_name.split(' ')[0] : 'CPU'}</span>
            </div>

            {/* Settings Action Button */}
            <button
              onClick={() => setActiveTab('settings')}
              className={`p-1.5 rounded-lg border transition-colors cursor-pointer ${
                activeTab === 'settings'
                  ? 'bg-violet-600/20 text-violet-300 border-violet-500/40'
                  : 'text-slate-400 hover:text-slate-200 bg-[#11131B] border-white/[0.06] hover:bg-[#171A25]'
              }`}
              title="Settings & Model Configuration"
            >
              <SettingsIcon className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="md:hidden flex overflow-x-auto border-t border-white/[0.05] bg-[#080910] px-3 py-1.5 gap-1">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`px-3 py-1 rounded-lg text-xs whitespace-nowrap font-medium transition-colors ${
              activeTab === item.id
                ? 'bg-[#171A25] text-violet-200 border border-white/[0.08]'
                : 'text-[#A2A6B8]'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>
    </header>
  );
};
