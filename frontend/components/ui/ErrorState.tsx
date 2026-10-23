import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Unable to load data",
  message,
  onRetry,
  className = "",
}) => {
  return (
    <div
      className={`p-6 rounded-2xl bg-rose-950/20 border border-rose-900/40 text-center max-w-lg mx-auto ${className}`}
      role="alert"
    >
      <div className="w-10 h-10 rounded-full bg-rose-900/40 text-rose-400 flex items-center justify-center mx-auto mb-3">
        <AlertCircle className="w-5 h-5" />
      </div>
      <h3 className="text-base font-semibold text-rose-300 mb-1">{title}</h3>
      <p className="text-xs text-neutral-400 leading-relaxed mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-neutral-850 hover:bg-neutral-800 text-xs font-medium text-neutral-200 border border-neutral-750 transition-colors focus:outline-none focus:ring-2 focus:ring-rose-500/50"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Try Again</span>
        </button>
      )}
    </div>
  );
};
