import React from "react";
import { Loader2 } from "lucide-react";

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = "Loading data...",
  className = "",
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center p-12 text-center text-neutral-400 ${className}`}
      role="status"
      aria-live="polite"
    >
      <Loader2 className="w-8 h-8 animate-spin text-amber-500 mb-3" />
      <p className="text-sm font-medium">{message}</p>
    </div>
  );
};
