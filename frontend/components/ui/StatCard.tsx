import React from "react";
import { EngineBadge } from "./EngineBadge";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode | React.ComponentType<{ className?: string }>;
  engine?: "neo4j" | "monetdb" | "fastapi" | "hybrid";
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  engine,
  className = "",
}) => {
  const renderIcon = () => {
    if (!icon) return null;
    if (React.isValidElement(icon)) return icon;
    const IconComp = icon as React.ComponentType<{ className?: string }>;
    return <IconComp className="h-4 w-4" />;
  };

  return (
    <div
      className={`p-5 rounded-2xl bg-neutral-900/60 border border-neutral-800/80 hover:border-neutral-700/80 transition-all duration-200 backdrop-blur-sm ${className}`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-neutral-400 tracking-wide uppercase">
          {title}
        </span>
        {icon && <div className="text-neutral-400">{renderIcon()}</div>}
      </div>
      <div className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
        {typeof value === "number" ? value.toLocaleString() : value}
      </div>
      {(subtitle || engine) && (
        <div className="mt-3 flex items-center justify-between gap-2 pt-2 border-t border-neutral-850/60 text-xs">
          {subtitle && <span className="text-neutral-400 truncate">{subtitle}</span>}
          {engine && <EngineBadge engine={engine} size="sm" />}
        </div>
      )}
    </div>
  );
};
