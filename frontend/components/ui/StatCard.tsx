import React from "react";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode | React.ComponentType<{ className?: string }>;
  accentColor?: "indigo" | "amber" | "emerald" | "purple" | "rose";
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  accentColor = "indigo",
  className = "",
}) => {
  const colorMap = {
    indigo: {
      iconBg: "bg-indigo-500/10 border-indigo-500/20 text-indigo-400 shadow-indigo-500/10",
      topGlow: "from-indigo-500/40 to-transparent",
      badge: "text-indigo-300 bg-indigo-500/10",
    },
    amber: {
      iconBg: "bg-amber-500/10 border-amber-500/20 text-amber-400 shadow-amber-500/10",
      topGlow: "from-amber-500/40 to-transparent",
      badge: "text-amber-300 bg-amber-500/10",
    },
    emerald: {
      iconBg: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400 shadow-emerald-500/10",
      topGlow: "from-emerald-500/40 to-transparent",
      badge: "text-emerald-300 bg-emerald-500/10",
    },
    purple: {
      iconBg: "bg-purple-500/10 border-purple-500/20 text-purple-400 shadow-purple-500/10",
      topGlow: "from-purple-500/40 to-transparent",
      badge: "text-purple-300 bg-purple-500/10",
    },
    rose: {
      iconBg: "bg-rose-500/10 border-rose-500/20 text-rose-400 shadow-rose-500/10",
      topGlow: "from-rose-500/40 to-transparent",
      badge: "text-rose-300 bg-rose-500/10",
    },
  };

  const currentTheme = colorMap[accentColor] || colorMap.indigo;

  const renderIcon = () => {
    if (!icon) return null;
    if (React.isValidElement(icon)) return icon;
    const IconComp = icon as React.ComponentType<{ className?: string }>;
    return <IconComp className="h-4 w-4" />;
  };

  return (
    <div
      className={`group relative overflow-hidden rounded-2xl border border-neutral-800/80 bg-gradient-to-b from-neutral-900/90 to-neutral-950/80 p-5 shadow-sm backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:border-neutral-700 hover:shadow-xl hover:shadow-black/50 ${className}`}
    >
      {/* Top subtle highlight line on hover */}
      <div
        className={`absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r opacity-0 transition-opacity duration-300 group-hover:opacity-100 ${currentTheme.topGlow}`}
      />

      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-neutral-400 tracking-wider uppercase">
          {title}
        </span>
        {icon && (
          <div
            className={`flex h-8 w-8 items-center justify-center rounded-lg border shadow-sm transition-transform duration-200 group-hover:scale-110 ${currentTheme.iconBg}`}
          >
            {renderIcon()}
          </div>
        )}
      </div>

      <div className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
        {typeof value === "number" ? value.toLocaleString() : value}
      </div>

      {subtitle && (
        <div className="mt-3 flex items-center gap-1.5 pt-2.5 border-t border-neutral-800/70 text-xs text-neutral-400">
          <span className="h-1.5 w-1.5 rounded-full bg-neutral-600 group-hover:bg-indigo-400 transition-colors" />
          <span className="truncate">{subtitle}</span>
        </div>
      )}
    </div>
  );
};
