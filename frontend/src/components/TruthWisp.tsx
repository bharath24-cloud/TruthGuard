import React, { useState, useEffect } from 'react';

export type WispState = 'idle' | 'focused' | 'typing' | 'verifying' | 'contradicted' | 'supported';

interface TruthWispProps {
  state?: WispState;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  subtle?: boolean;
}

export const TruthWisp: React.FC<TruthWispProps> = ({
  state = 'idle',
  size = 'md',
  className = '',
  subtle = false,
}) => {
  const [isBlinking, setIsBlinking] = useState(false);
  const [satisfactionPulse, setSatisfactionPulse] = useState(false);
  const [microGazeX, setMicroGazeX] = useState(0);
  const [microGazeY, setMicroGazeY] = useState(0);

  // Natural intermittent blinking cycle (3.6s - 5.8s natural variance)
  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;

    const scheduleNextBlink = () => {
      const delay = Math.random() * 2200 + 3600;
      timeoutId = setTimeout(() => {
        setIsBlinking(true);
        setTimeout(() => {
          setIsBlinking(false);
          scheduleNextBlink();
        }, 140);
      }, delay);
    };

    scheduleNextBlink();
    return () => clearTimeout(timeoutId);
  }, []);

  // Subtle natural micro-saccades during idle to feel truly alive
  useEffect(() => {
    let saccadeTimer: ReturnType<typeof setTimeout>;

    const scheduleSaccade = () => {
      const delay = Math.random() * 3000 + 2500;
      saccadeTimer = setTimeout(() => {
        if (state === 'idle') {
          // Tiny organic ocular drift (-1.2px to +1.2px)
          setMicroGazeX((Math.random() - 0.5) * 2.4);
          setMicroGazeY((Math.random() - 0.5) * 1.6);
        }
        scheduleSaccade();
      }, delay);
    };

    scheduleSaccade();
    return () => clearTimeout(saccadeTimer);
  }, [state]);

  // Satisfying celebration pulse upon verified completion
  useEffect(() => {
    if (state === 'supported') {
      setSatisfactionPulse(true);
      const timer = setTimeout(() => setSatisfactionPulse(false), 2400);
      return () => clearTimeout(timer);
    }
  }, [state]);

  // Dimension scaling
  const dimensions = {
    sm: { width: 36, height: 44, viewBox: '0 0 200 240' },
    md: { width: 110, height: 132, viewBox: '0 0 200 240' },
    lg: { width: 190, height: 228, viewBox: '0 0 200 240' },
  }[size];

  // Interaction flags
  const isFocused = state === 'focused' || state === 'typing';
  const isVerifying = state === 'verifying';
  const isContradicted = state === 'contradicted';
  const isSupported = state === 'supported';

  // Gaze tracking: shifts toward user input when focused, or performs subtle micro-saccades when idle
  const gazeX = isFocused ? 3.2 : microGazeX;
  const gazeY = isFocused ? 2.0 : microGazeY;
  const eyeScaleY = isBlinking ? 0.06 : isContradicted ? 0.65 : 1.0;

  // Authentic state-driven ocular palette
  const getEyeCoreColor = () => {
    if (isContradicted) return '#F87171'; // Discerning alert
    if (isVerifying) return '#93C5FD';    // Active analytical
    if (isSupported) return '#6EE7B7';    // Serene affirmed
    return '#7AA2FF';                     // Natural cool electric blue
  };

  const getInternalAuraColor = () => {
    if (isContradicted) return 'rgba(239, 68, 68, 0.22)';
    if (isVerifying) return 'rgba(122, 162, 255, 0.24)';
    if (isSupported) return 'rgba(52, 211, 153, 0.20)';
    return 'rgba(139, 92, 246, 0.16)';
  };

  return (
    <div
      className={`relative inline-flex items-center justify-center select-none ${className}`}
      style={{ width: dimensions.width, height: dimensions.height }}
      role="img"
      aria-label={`TruthGuard Living Mascot - The Truth Wisp in ${state} state`}
    >
      {/* Restrained Soft Aura Behind Core */}
      {!subtle && (
        <div
          className="absolute inset-1 rounded-full blur-2xl transition-all duration-700 pointer-events-none"
          style={{
            background: `radial-gradient(circle, ${getInternalAuraColor()} 0%, transparent 70%)`,
            transform: `scale(${isVerifying ? 1.25 : isFocused ? 1.15 : 1.0})`,
            opacity: isVerifying ? 0.85 : 0.55,
          }}
        />
      )}

      {/* SVG The Truth Wisp */}
      <svg
        viewBox={dimensions.viewBox}
        width={dimensions.width}
        height={dimensions.height}
        className={`relative z-10 transition-transform duration-500 ease-out ${
          isFocused
            ? 'rotate-2 translate-x-1'
            : satisfactionPulse
            ? '-translate-y-2 scale-105'
            : 'animate-wisp-float'
        }`}
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* 1. Translucent Liquid Obsidian Body Gradient */}
          <linearGradient id={`wispObsidianBody_${size}`} x1="45" y1="20" x2="155" y2="225" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#C4B5FD" stopOpacity="0.82" />
            <stop offset="22%" stopColor="#8B5CF6" stopOpacity="0.65" />
            <stop offset="55%" stopColor="#1E1B4B" stopOpacity="0.75" />
            <stop offset="85%" stopColor="#0B0C14" stopOpacity="0.92" />
            <stop offset="100%" stopColor="#171A25" stopOpacity="0.85" />
          </linearGradient>

          {/* 2. Liquid Ribbon Extension Flow Gradient */}
          <linearGradient id={`wispRibbonStream_${size}`} x1="70" y1="95" x2="135" y2="235" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0.75" />
            <stop offset="45%" stopColor="#7AA2FF" stopOpacity="0.45" />
            <stop offset="85%" stopColor="#7AA2FF" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#7AA2FF" stopOpacity="0.02" />
          </linearGradient>

          {/* 3. Deep Obsidian Face Visor */}
          <radialGradient id={`wispVisorCore_${size}`} cx="100" cy="74" r="34" fx="94" fy="68" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0D0E18" stopOpacity="0.98" />
            <stop offset="65%" stopColor="#080910" stopOpacity="0.99" />
            <stop offset="100%" stopColor="#1E1B4B" stopOpacity="0.88" />
          </radialGradient>

          {/* 4. Specular Edge Fresnel Highlight */}
          <linearGradient id={`wispFresnelRim_${size}`} x1="65" y1="18" x2="135" y2="110" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.85" />
            <stop offset="35%" stopColor="#C4B5FD" stopOpacity="0.4" />
            <stop offset="75%" stopColor="#7AA2FF" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0.35" />
          </linearGradient>

          {/* 5. Subsurface Internal Light Shimmer */}
          <radialGradient id={`wispCausticGlow_${size}`} cx="95" cy="78" r="42" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={isContradicted ? '#EF4444' : isVerifying ? '#7AA2FF' : '#8B5CF6'} stopOpacity="0.32" />
            <stop offset="50%" stopColor={isContradicted ? '#991B1B' : '#7AA2FF'} stopOpacity="0.12" />
            <stop offset="100%" stopColor="transparent" stopOpacity="0" />
          </radialGradient>

          {/* 6. Eye Radial Core */}
          <radialGradient id={`wispEyeRadiance_${size}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="1" />
            <stop offset="42%" stopColor={getEyeCoreColor()} stopOpacity="0.95" />
            <stop offset="100%" stopColor={getEyeCoreColor()} stopOpacity="0" />
          </radialGradient>

          {/* 7. Ocular Soft Diffusion Filter */}
          <filter id={`wispEyeGlowFilter_${size}`} x="-35%" y="-35%" width="170%" height="170%">
            <feGaussianBlur stdDeviation="1.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* ========================================================= */}
        {/* DEPTH PLANE 1: Dorsal Ribbon (Behind Right)             */}
        {/* ========================================================= */}
        <path
          d="M 126 108 C 146 126 164 144 156 176 C 150 198 138 208 129 201 C 121 194 129 176 132 153 C 134 134 124 122 120 114 Z"
          fill={`url(#wispRibbonStream_${size})`}
          stroke="rgba(196, 181, 253, 0.22)"
          strokeWidth="0.8"
          className="animate-wisp-dorsal transition-all duration-700"
        />

        {/* ========================================================= */}
        {/* DEPTH PLANE 2: Lateral Ribbon (Curling Left Flank)       */}
        {/* ========================================================= */}
        <path
          d="M 64 82 C 46 95 32 110 34 132 C 36 146 45 148 48 141 C 52 130 46 118 53 104 C 57 93 62 87 64 82 Z"
          fill={`url(#wispRibbonStream_${size})`}
          stroke="rgba(122, 162, 255, 0.2)"
          strokeWidth="0.8"
          className="animate-wisp-lateral transition-all duration-700"
        />

        {/* ========================================================= */}
        {/* DEPTH PLANE 3: Ventral Ribbon (Flowing Undulating Tail)  */}
        {/* ========================================================= */}
        <path
          d="M 88 115 C 80 142 66 172 70 198 C 73 216 86 226 94 218 C 102 210 94 195 92 178 C 90 156 96 138 98 122 Z"
          fill={`url(#wispRibbonStream_${size})`}
          stroke={`url(#wispFresnelRim_${size})`}
          strokeWidth="0.9"
          className="animate-wisp-ventral transition-all duration-700"
        />

        {/* ========================================================= */}
        {/* DEPTH PLANE 4: Asymmetrical Sculptural Head & Body Core   */}
        {/* ========================================================= */}
        <path
          d="M 112 22 C 84 34 62 60 62 82 C 62 104 74 122 94 124 C 114 126 134 110 134 82 C 134 52 128 32 112 22 Z"
          fill={`url(#wispObsidianBody_${size})`}
          stroke={`url(#wispFresnelRim_${size})`}
          strokeWidth="1.2"
          className="transition-all duration-700"
        />

        {/* ========================================================= */}
        {/* DEPTH PLANE 5: Subsurface Caustic Light Wave             */}
        {/* ========================================================= */}
        <path
          d="M 108 32 C 88 44 74 66 74 84 C 74 100 84 114 98 116 C 112 118 124 104 124 82 C 124 58 120 42 108 32 Z"
          fill={`url(#wispCausticGlow_${size})`}
          className="animate-wisp-light transition-all duration-500"
        />

        {/* ========================================================= */}
        {/* DEPTH PLANE 6: Smooth Dark Obsidian Visor Plate          */}
        {/* ========================================================= */}
        <ellipse
          cx="99"
          cy="75"
          rx="27"
          ry="25"
          transform="rotate(-2 99 75)"
          fill={`url(#wispVisorCore_${size})`}
          stroke="rgba(255, 255, 255, 0.11)"
          strokeWidth="0.8"
        />

        {/* Liquid Crest Specular Fresnel Glint (Top Arc) */}
        <path
          d="M 76 52 C 84 38 98 28 112 24"
          stroke="rgba(255, 255, 255, 0.7)"
          strokeWidth="1.3"
          strokeLinecap="round"
        />

        {/* ========================================================= */}
        {/* DEPTH PLANE 7: Expressive Luminous Ocular System         */}
        {/* ========================================================= */}
        <g
          transform={`translate(${gazeX}, ${gazeY})`}
          className="transition-transform duration-200 ease-out"
        >
          {isSupported ? (
            /* Pleased serene crescent arcs (^ ^) upon verified completion */
            <g stroke={getEyeCoreColor()} strokeWidth="2.2" strokeLinecap="round" filter={`url(#wispEyeGlowFilter_${size})`}>
              <path d="M 82 74 Q 87 67 92 74" />
              <path d="M 106 73 Q 111 66 116 73" />
            </g>
          ) : (
            /* Living expressive almond-shaped eyes with articulated blinking & gaze tracking */
            <g filter={`url(#wispEyeGlowFilter_${size})`}>
              {/* Left Eye */}
              <g
                style={{
                  transformOrigin: '87px 74px',
                  transform: `scaleY(${eyeScaleY})`,
                  transition: 'transform 0.12s cubic-bezier(0.4, 0, 0.2, 1)',
                }}
              >
                <ellipse cx="87" cy="74" rx="3.8" ry="5.2" fill={`url(#wispEyeRadiance_${size})`} />
                <circle cx="86" cy="72.5" r="1.2" fill="#FFFFFF" />
              </g>

              {/* Right Eye */}
              <g
                style={{
                  transformOrigin: '111px 73px',
                  transform: `scaleY(${eyeScaleY})`,
                  transition: 'transform 0.12s cubic-bezier(0.4, 0, 0.2, 1)',
                }}
              >
                <ellipse cx="111" cy="73" rx="3.8" ry="5.2" fill={`url(#wispEyeRadiance_${size})`} />
                <circle cx="110" cy="71.5" r="1.2" fill="#FFFFFF" />
              </g>
            </g>
          )}

          {/* Delicate distinctive facial expression / micro-smile */}
          <path
            d={
              isContradicted
                ? 'M 95 86 Q 99 85 103 86'   // Discerning neutral line
                : isSupported
                ? 'M 93 85 Q 99 90 105 85'   // Serene pleased micro-smile
                : 'M 94 86 Q 99 88.5 104 86' // Calm observant micro-curve
            }
            stroke={isSupported ? '#6EE7B7' : 'rgba(196, 181, 253, 0.45)'}
            strokeWidth="1.1"
            strokeLinecap="round"
            fill="none"
            className="transition-all duration-300"
          />
        </g>

        {/* ========================================================= */}
        {/* DEPTH PLANE 8: Detaching & Re-absorbing Motes            */}
        {/* ========================================================= */}
        {!subtle && (
          <g>
            {/* Mote 1: Detaches from ventral ribbon tail and drifts upward */}
            <circle
              cx="92"
              cy="210"
              r="1.6"
              fill="#7AA2FF"
              className="animate-wisp-mote-1 pointer-events-none"
            />
            {/* Mote 2: Detaches from lateral ribbon and loops near waist */}
            <circle
              cx="46"
              cy="132"
              r="1.4"
              fill="#C4B5FD"
              className="animate-wisp-mote-2 pointer-events-none"
            />
          </g>
        )}
      </svg>
    </div>
  );
};
