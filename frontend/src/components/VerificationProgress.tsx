import React from 'react';
import { Layers, Search, ShieldCheck, CheckCircle2, Loader2 } from 'lucide-react';

interface VerificationProgressProps {
  currentStage: number; // 1: Extracting Claims, 2: Searching Evidence, 3: Verifying Claims, 4: Preparing Results
  stageText?: string;
}

export const VerificationProgress: React.FC<VerificationProgressProps> = ({
  currentStage,
  stageText,
}) => {
  const stages = [
    { id: 1, label: 'Decomposing Claims', icon: Layers },
    { id: 2, label: 'Retrieving Evidence', icon: Search },
    { id: 3, label: 'NLI Inference', icon: ShieldCheck },
    { id: 4, label: 'Calibrating Results', icon: CheckCircle2 },
  ];

  return (
    <div className="w-full py-4 px-5 rounded-2xl bg-[#11131B] border border-white/[0.06] shadow-lg space-y-3">
      {/* Top Status */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <Loader2 className="w-3.5 h-3.5 text-violet-400 animate-spin" />
          <span className="font-medium text-violet-300">
            {stageText || 'Auditing claim veracity...'}
          </span>
        </div>
        <span className="text-[11px] font-mono text-slate-500">
          Step {Math.min(currentStage, 4)} of 4
        </span>
      </div>

      {/* 4-Stage Horizontal Flow */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {stages.map((stage, idx) => {
          const Icon = stage.icon;
          const isCompleted = currentStage > stage.id;
          const isActive = currentStage === stage.id;
          const isPending = currentStage < stage.id;

          return (
            <div
              key={stage.id}
              className={`flex items-center gap-2.5 p-2 rounded-xl border transition-all ${
                isActive
                  ? 'bg-[#171A25] border-violet-500/40 text-violet-200'
                  : isCompleted
                  ? 'bg-transparent border-white/[0.04] text-slate-300'
                  : 'bg-transparent border-transparent text-slate-600'
              }`}
            >
              <div
                className={`w-6 h-6 rounded-lg flex items-center justify-center shrink-0 transition-colors ${
                  isActive
                    ? 'bg-violet-600/30 text-violet-300'
                    : isCompleted
                    ? 'bg-emerald-950/40 text-emerald-400'
                    : 'bg-[#080910] text-slate-600'
                }`}
              >
                <Icon className="w-3 h-3" />
              </div>

              <span className={`text-xs truncate ${isActive ? 'font-medium text-white' : isCompleted ? 'text-slate-300' : 'text-slate-600'}`}>
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
