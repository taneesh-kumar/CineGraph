import React from "react";
import { FolderSearch } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  action,
  actionLabel,
  onAction,
  className = "",
}) => {
  const finalActionLabel = action?.label || actionLabel;
  const finalActionClick = action?.onClick || onAction;

  return (
    <div
      className={`p-10 rounded-2xl bg-neutral-900/40 border border-neutral-850 text-center max-w-md mx-auto ${className}`}
    >
      <div className="w-12 h-12 rounded-2xl bg-neutral-850 text-neutral-400 flex items-center justify-center mx-auto mb-3">
        <FolderSearch className="w-6 h-6" />
      </div>
      <h3 className="text-base font-semibold text-neutral-200 mb-1">{title}</h3>
      <p className="text-xs text-neutral-400 leading-relaxed mb-4">{description}</p>
      {finalActionLabel && finalActionClick && (
        <button
          onClick={finalActionClick}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-xs font-medium text-indigo-400 border border-indigo-500/30 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
        >
          {finalActionLabel}
        </button>
      )}
    </div>
  );
};
