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
  const isCompleted = status === 'completed';
  const isRunning   = status === 'running';
  const isFailed    = status === 'failed';
  const isPending   = status === 'pending';

  const statusIcon = () => {
    if (isCompleted) return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
    if (isRunning)   return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
    if (isFailed)    return <XCircle className="w-5 h-5 text-red-400" />;
    return <Clock className="w-5 h-5 text-gray-300" />;
  };

  return (
    <div className={clsx(
      "card p-5 transition-all duration-300 animate-slide-up",
      isRunning  && "ring-2 ring-blue-400/40 shadow-md border-blue-100",
      isCompleted && "border-emerald-100",
      isFailed   && "border-red-100",
    )}>
      <div className="flex items-center gap-4">
        {/* Stage number bubble */}
        <div className={clsx(
          "w-9 h-9 rounded-xl flex items-center justify-center font-bold text-sm shrink-0 transition-colors",
          isCompleted ? "bg-emerald-50 text-emerald-700" :
          isRunning   ? "bg-blue-50 text-blue-700" :
          isFailed    ? "bg-red-50 text-red-600" :
          "bg-gray-100 text-gray-400"
        )}>
          {stageNum}
        </div>

        {/* Title + description */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className={clsx(
              "font-semibold text-sm",
              isPending ? "text-gray-400" : "text-gray-900"
            )}>{title}</h3>
            {statusIcon()}
          </div>
          <p className="text-xs text-gray-400 mt-0.5 truncate">{description}</p>
        </div>

        {/* Count */}
        {count !== undefined && (isCompleted || isRunning) && (
          <div className="text-right shrink-0">
            <div className={clsx(
              "text-xl font-bold",
              isCompleted ? "text-emerald-600" :
              isRunning   ? "text-blue-600"   : "text-gray-900"
            )}>{count}</div>
            <div className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">{countLabel}</div>
          </div>
        )}
      </div>

      {/* Running shimmer bar */}
      {isRunning && (
        <div className="mt-4 h-1 bg-gray-100 rounded-full overflow-hidden">
          <div className="h-full bg-blue-400 rounded-full animate-[pulse_1.5s_ease-in-out_infinite] w-1/2" />
        </div>
      )}
    </div>
  );
}
