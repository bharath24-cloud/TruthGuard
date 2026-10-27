import React from 'react';
import { 
  FileCheck2, 
  AlertTriangle, 
  CheckCircle2, 
  HelpCircle, 
  ShieldAlert, 
  ArrowUpRight, 
  PlusCircle, 
  FolderPlus,
  Activity,
  Layers,
  Sparkles
} from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis } from 'recharts';
import { VerificationReport } from '../types';

interface DashboardProps {
  reports: VerificationReport[];
  setActiveTab: (tab: string) => void;
  onSelectReport: (report: VerificationReport) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ reports, setActiveTab, onSelectReport }) => {
  // Aggregate statistics across all verification runs
  const totalRuns = reports.length;
  const totalClaims = reports.reduce((acc, r) => acc + r.total_claims, 0);
  const supportedClaims = reports.reduce((acc, r) => acc + r.supported_claims, 0);
  const contradictedClaims = reports.reduce((acc, r) => acc + r.contradicted_claims, 0);
  const insufficientClaims = reports.reduce((acc, r) => acc + r.insufficient_claims, 0);
  const conflictingClaims = reports.reduce((acc, r) => acc + r.conflicting_claims, 0);

  const avgHallucinationScore = totalRuns > 0
    ? (reports.reduce((acc, r) => acc + r.hallucination_score, 0) / totalRuns)
    : 0;

  const pieData = [
    { name: 'Supported', value: supportedClaims, color: '#34D399' },
    { name: 'Contradicted', value: contradictedClaims, color: '#F87171' },
    { name: 'Insufficient Evidence', value: insufficientClaims, color: '#FBBF24' },
    { name: 'Conflicting Evidence', value: conflictingClaims, color: '#C084FC' }
  ].filter(d => d.value > 0);

  const barData = reports.slice(0, 6).reverse().map((r, i) => ({
    name: `Run #${reports.length - i}`,
    risk: Math.round(r.hallucination_score * 100),
    claims: r.total_claims
  }));

  return (
    <div className="space-y-8">
      {/* Top Hero Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 sm:p-7 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-2xl">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-xs font-medium mb-2">
            <Sparkles className="w-3 h-3 text-violet-400" />
            <span>Telemetry & Audit Analytics</span>
          </div>
          <h1 className="text-2xl font-bold text-[#F4F4FA] flex items-center gap-2">
            Verification & Hallucination Overview
          </h1>
          <p className="text-[#94A3B8] text-sm mt-1 max-w-xl">
            Live evaluation analytics across all atomic assertions verified with DeBERTa NLI and FAISS semantic retrieval.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('verify')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium text-xs transition-all shadow-[0_0_16px_rgba(139,92,246,0.3)] cursor-pointer"
          >
            <PlusCircle className="w-4 h-4" />
            New Verification
          </button>
          <button
            onClick={() => setActiveTab('documents')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#080910] hover:bg-[#1a1d2d] text-slate-300 font-medium text-xs transition-all border border-white/[0.08] cursor-pointer"
          >
            <FolderPlus className="w-4 h-4 text-violet-400" />
            Manage Corpora
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {/* Total Runs */}
        <div className="p-4 sm:p-5 rounded-2xl bg-[#11131D]/80 border border-white/[0.07] shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Runs</span>
            <Activity className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-[#F4F4FA] mt-2">{totalRuns}</div>
          <div className="text-[11px] text-[#94A3B8] mt-1">Total analyzed runs</div>
        </div>

        {/* Total Claims */}
        <div className="p-4 sm:p-5 rounded-2xl bg-[#11131D]/80 border border-white/[0.07] shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Claims</span>
            <Layers className="w-4 h-4 text-violet-400" />
          </div>
          <div className="text-2xl font-bold text-[#F4F4FA] mt-2">{totalClaims}</div>
          <div className="text-[11px] text-[#94A3B8] mt-1">Extracted assertions</div>
        </div>

        {/* Supported */}
        <div className="p-4 sm:p-5 rounded-2xl bg-emerald-950/15 border border-emerald-500/20 shadow-sm">
          <div className="flex items-center justify-between text-emerald-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Supported</span>
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div className="text-2xl font-bold text-emerald-300 mt-2">{supportedClaims}</div>
          <div className="text-[11px] text-[#94A3B8] mt-1">
            {totalClaims > 0 ? `${Math.round((supportedClaims / totalClaims) * 100)}% of claims` : 'No data'}
          </div>
        </div>

        {/* Contradicted */}
        <div className="p-4 sm:p-5 rounded-2xl bg-rose-950/15 border border-rose-500/20 shadow-sm">
          <div className="flex items-center justify-between text-rose-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Contradicted</span>
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div className="text-2xl font-bold text-rose-300 mt-2">{contradictedClaims}</div>
          <div className="text-[11px] text-[#94A3B8] mt-1">
            {totalClaims > 0 ? `${Math.round((contradictedClaims / totalClaims) * 100)}% of claims` : 'No data'}
          </div>
        </div>

        {/* Insufficient Evidence */}
        <div className="p-4 sm:p-5 rounded-2xl bg-amber-950/15 border border-amber-500/20 shadow-sm">
          <div className="flex items-center justify-between text-amber-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Unverified</span>
            <HelpCircle className="w-4 h-4" />
          </div>
          <div className="text-2xl font-bold text-amber-300 mt-2">{insufficientClaims}</div>
          <div className="text-[11px] text-[#94A3B8] mt-1">Insufficient evidence</div>
        </div>

        {/* Hallucination Risk Score */}
        <div className="p-4 sm:p-5 rounded-2xl bg-[#11131D]/80 border border-white/[0.07] shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Avg Risk</span>
            <ShieldAlert className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-[#F4F4FA] mt-2">
            {(avgHallucinationScore * 100).toFixed(1)}%
          </div>
          <div className="text-[11px] text-[#94A3B8] mt-1">Composite risk index</div>
        </div>
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Verdict Distribution Chart */}
        <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-base font-semibold text-[#F4F4FA]">Claim Verification Verdict Distribution</h3>
            <p className="text-xs text-[#94A3B8] mt-1">Natural Language Inference breakdown across all atomic assertions.</p>
          </div>
          
          <div className="h-64 my-4 flex items-center justify-center">
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={95}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#080910', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px' }}
                    itemStyle={{ color: '#F4F4FA' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-slate-500 text-sm">
                No verification data available yet. Run a verification to populate analytics.
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-3 border-t border-white/[0.06] text-xs">
            <div className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block" />
              <span>Supported: {supportedClaims}</span>
            </div>
            <div className="flex items-center gap-1.5 text-rose-400">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-400 inline-block" />
              <span>Contradicted: {contradictedClaims}</span>
            </div>
            <div className="flex items-center gap-1.5 text-amber-400">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" />
              <span>Unverified: {insufficientClaims}</span>
            </div>
            <div className="flex items-center gap-1.5 text-purple-400">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-400 inline-block" />
              <span>Conflict: {conflictingClaims}</span>
            </div>
          </div>
        </div>

        {/* Recent Hallucination Risk Scores */}
        <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-base font-semibold text-[#F4F4FA]">Recent Verification Hallucination Scores (%)</h3>
            <p className="text-xs text-[#94A3B8] mt-1">Lower scores represent higher factual groundedness.</p>
          </div>

          <div className="h-64 my-4 flex items-center justify-center">
            {barData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#080910', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px' }}
                    itemStyle={{ color: '#F4F4FA' }}
                  />
                  <Bar dataKey="risk" fill="#8B5CF6" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-slate-500 text-sm">
                No recent runs recorded yet.
              </div>
            )}
          </div>

          <div className="text-xs text-[#94A3B8] pt-3 border-t border-white/[0.06]">
            Risk formulation: 70% Contradiction Rate + 30% Unverified Claim Rate
          </div>
        </div>
      </div>

      {/* Recent Verification Activity Table */}
      <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-[#F4F4FA]">Recent Verification Activity</h3>
            <p className="text-xs text-[#94A3B8]">Click any run to view claim spans, evidence passages, and grounded corrections.</p>
          </div>
          {reports.length > 0 && (
            <button
              onClick={() => setActiveTab('history')}
              className="text-xs font-medium text-violet-400 hover:text-violet-300 flex items-center gap-1 transition-colors"
            >
              View Full History <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {reports.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-white/[0.08] rounded-2xl bg-[#080910]/40">
            <FileCheck2 className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h4 className="text-sm font-semibold text-slate-300">No verifications performed yet</h4>
            <p className="text-xs text-[#94A3B8] max-w-sm mx-auto mt-1 mb-4">
              Upload reference documents to your library or use the FEVER knowledge base, then verify answers with real evidence.
            </p>
            <button
              onClick={() => setActiveTab('verify')}
              className="px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium transition-all shadow-[0_0_14px_rgba(139,92,246,0.25)] cursor-pointer"
            >
              Start First Verification
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-[#080910] text-slate-400 border-b border-white/[0.06]">
                <tr>
                  <th className="py-3 px-4">Question</th>
                  <th className="py-3 px-4">Model</th>
                  <th className="py-3 px-4">Claims</th>
                  <th className="py-3 px-4">Verdicts (S / C / U)</th>
                  <th className="py-3 px-4">Risk Score</th>
                  <th className="py-3 px-4">Latency</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.05]">
                {reports.slice(0, 5).map((r) => (
                  <tr key={r.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 font-medium text-[#F4F4FA] max-w-xs truncate">
                      {r.question}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-400">{r.model_used}</td>
                    <td className="py-3.5 px-4 text-xs font-medium">{r.total_claims}</td>
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
                    <td className="py-3.5 px-4 text-xs text-slate-400">{r.latency_ms.toFixed(0)}ms</td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => onSelectReport(r)}
                        className="px-2.5 py-1 rounded-lg bg-[#080910] hover:bg-violet-600/20 text-xs font-medium text-slate-200 border border-white/[0.08] hover:border-violet-500/40 transition-all cursor-pointer"
                      >
                        Inspect
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
