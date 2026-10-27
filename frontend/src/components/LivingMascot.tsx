import React from 'react';
import { TruthWisp, WispState } from './TruthWisp';

export type MascotState = WispState;

export const LivingMascot: React.FC<{
  state?: MascotState;
  stage?: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  subtle?: boolean;
}> = (props) => {
  return <TruthWisp {...props} />;
};

export { TruthWisp };
