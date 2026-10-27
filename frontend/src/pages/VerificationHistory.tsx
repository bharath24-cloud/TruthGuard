import React, { useState } from 'react';
import { 
  History, 
  Search, 
  ArrowUpRight, 
  Clock, 
  Download,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Sparkles
} from 'lucide-react';
import { VerificationReport } from '../types';

interface VerificationHistoryProps {
  reports: VerificationReport[];
  onSelectReport: (report: VerificationReport) => void;
  setActiveTab: (tab: string) => void;
}

export const VerificationHistory: React.FC<VerificationHistoryProps> = ({
  reports,
  onSelectReport,
  setActiveTab
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterVerdict, setFilterVerdict] = useState<string>('all');

  const filteredReports = reports.filter(r => {
    const matchesSearch = r.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          r.model_used.toLowerCase().includes(searchTerm.toLowerCase());
    if (filterVerdict === 'has_contradictions') {
      return matchesSearch && r.contradicted_claims > 0;
    }
    if (filterVerdict === 'clean') {
      return matchesSearch && r.contradicted_claims === 0 && r.hallucination_score === 0;
    }
    return matchesSearch;
  });

  const exportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reports, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `truthguard_history_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 sm:p-7 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-2xl">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-xs font-medium mb-2">
            <Sparkles className="w-3 h-3 text-violet-400" />
            <span>Audit Trail & Persistence</span>
          </div>
          <h2 className="text-xl font-bold text-[#F4F4FA] flex items-center gap-2">
            <History className="w-5 h-5 text-violet-400" />
            Verification History & Audit Logs
          </h2>
          <p className="text-xs text-[#94A3B8] mt-1 max-w-xl">
            Persisted record of all claim decompositions, evidence matches, NLI inference scores, and grounded corrections.
          </p>
        </div>

        {reports.length > 0 && (
          <button
            onClick={exportJSON}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#080910] hover:bg-[#1a1d2d] text-slate-200 border border-white/[0.08] text-xs font-semibold transition-all cursor-pointer"
          >
            <Download className="w-4 h-4 text-violet-400" />
            Export Audit Logs (JSON)
          </button>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-[#11131D]/80 border border-white/[0.07] flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search questions or models..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-violet-500/50"
          />
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto text-xs">
          <span className="text-[#94A3B8]">Filter:</span>
          <select
            value={filterVerdict}
            onChange={(e) => setFilterVerdict(e.target.value)}
            className="px-3 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-slate-200 focus:outline-none cursor-pointer"
          >
            <option value="all">All Runs ({reports.length})</option>
            <option value="has_contradictions">With Contradictions</option>
            <option value="clean">100% Grounded</option>
          </select>
        </div>
      </div>

      {/* Runs Table */}
      <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl">
        {filteredReports.length === 0 ? (
          <div className="text-center py-16 text-[#94A3B8] text-sm">
            <Clock className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p>No verification history found matching your filters.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-[#080910] text-slate-400 border-b border-white/[0.06]">
                <tr>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Question</th>
                  <th className="py-3 px-4">Model</th>
                  <th className="py-3 px-4">Claims</th>
                  <th className="py-3 px-4">Verdicts (S / C / U)</th>
                  <th className="py-3 px-4">Hallucination Risk</th>
                  <th className="py-3 px-4">Latency</th>
                  <th className="py-3 px-4 text-right">Report</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.05]">
                {filteredReports.map((r) => (
                  <tr key={r.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-400 whitespace-nowrap">
                      {new Date(r.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-[#F4F4FA] max-w-xs truncate">
                      {r.question}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-400">
                      {r.model_used}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-medium">
                      {r.total_claims}
                    </td>
                    <td className="py-3.5 px-4 text-xs">
                      <span className="text-emerald-400 font-semibold">{r.supported_claims}</span> /{' '}
                      <span className="text-rose-400 font-semibold">{r.contradicted_claims}</span> /{' '}
                      <span className="text-amber-400 font-semibold">{r.insufficient_claims}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`inline-flex px-2 py-0.5 rounded text-xs font-semibold ${
                        r.hallucination_score > 0.4
                          ? 'bg-rose-950/50 text-rose-300 border border-rose-500/30'
                          : r.hallucination_score > 0.15
                          ? 'bg-amber-950/50 text-amber-300 border border-amber-500/30'
                          : 'bg-emerald-950/50 text-emerald-300 border border-emerald-500/30'
                      }`}>
                        {(r.hallucination_score * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-400">
                      {r.latency_ms.toFixed(0)}ms
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => {
                          onSelectReport(r);
                          setActiveTab('verify');
                        }}
                        className="px-3 py-1 rounded-lg bg-[#080910] hover:bg-violet-600/20 text-xs font-medium text-violet-300 border border-white/[0.08] hover:border-violet-500/40 transition-colors inline-flex items-center gap-1 cursor-pointer"
                      >
                        Inspect <ArrowUpRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
