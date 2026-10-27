import React from 'react';

export const AtmosphericBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden" aria-hidden="true">
      {/* Deep Near-Black Base */}
      <div className="absolute inset-0 bg-[#080910]" />

      {/* Extremely Faint, Soft Radial Atmosphere Behind Workspace */}
      <div
        className="absolute top-[-10%] left-[15%] w-[700px] h-[700px] rounded-full blur-[160px] opacity-[0.07] pointer-events-none"
        style={{
          background: 'radial-gradient(circle, #8B5CF6 0%, #7AA2FF 40%, transparent 70%)',
        }}
      />

      {/* Subtle Atmospheric Vignette */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse at 50% 30%, transparent 60%, rgba(8, 9, 16, 0.6) 100%)',
        }}
      />
    </div>
  );
};
