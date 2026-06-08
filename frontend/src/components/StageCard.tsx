import clsx from 'clsx';
import { CheckCircle2, Loader2, Clock, XCircle } from 'lucide-react';

interface StageCardProps {
  stageNum: number;
  title: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  count?: number;
  countLabel?: string;
}

export default function StageCard({ stageNum, title, description, status, count, countLabel }: StageCardProps) {
  
  const getStatusIcon = () => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="h-6 w-6 text-emerald-500" />;
      case 'running': return <Loader2 className="h-6 w-6 text-brand-500 animate-spin" />;
      case 'failed': return <XCircle className="h-6 w-6 text-rose-500" />;
      default: return <Clock className="h-6 w-6 text-slate-500" />;
    }
  };

  return (
    <div className={clsx(
      "p-6 rounded-2xl transition-all duration-500 relative overflow-hidden",
      status === 'running' ? "bg-slate-800 border-2 border-brand-500/50 shadow-lg shadow-brand-500/10" : "glass-panel"
    )}>
      {status === 'running' && (
        <div className="absolute inset-0 bg-gradient-to-r from-brand-500/0 via-brand-500/5 to-brand-500/0 animate-[pulse_2s_ease-in-out_infinite]" />
      )}
      
      <div className="flex items-start justify-between relative z-10">
        <div className="flex items-center space-x-4">
          <div className={clsx(
            "w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg",
            status === 'completed' ? "bg-emerald-500/20 text-emerald-400" :
            status === 'running' ? "bg-brand-500/20 text-brand-400" :
            status === 'failed' ? "bg-rose-500/20 text-rose-400" :
            "bg-slate-800 text-slate-500"
          )}>
            {stageNum}
          </div>
          <div>
            <h3 className="font-semibold text-lg text-slate-200">{title}</h3>
            <p className="text-slate-400 text-sm mt-1">{description}</p>
          </div>
        </div>
        
        <div className="flex flex-col items-end space-y-2">
          {getStatusIcon()}
          {count !== undefined && (status === 'completed' || status === 'running') && (
            <div className="text-right">
              <span className="block text-2xl font-bold text-slate-100">{count}</span>
              <span className="block text-xs text-slate-400 uppercase tracking-wider">{countLabel}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
