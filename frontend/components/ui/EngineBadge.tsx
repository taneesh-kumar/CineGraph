import React from "react";

interface EngineBadgeProps {
  engine: "neo4j" | "monetdb" | "fastapi" | "hybrid";
  size?: "sm" | "md";
  showIcon?: boolean;
  className?: string;
}

export const EngineBadge: React.FC<EngineBadgeProps> = ({
  engine,
  size = "sm",
  showIcon = true,
  className = "",
}) => {
  const configs = {
    neo4j: {
      label: "Neo4j Graph",
      classes:
        "bg-amber-950/60 text-amber-300 border-amber-800/60 hover:border-amber-700/80",
      dot: "bg-amber-400",
    },
    monetdb: {
      label: "MonetDB Columnar",
      classes:
        "bg-indigo-950/60 text-indigo-300 border-indigo-800/60 hover:border-indigo-700/80",
      dot: "bg-indigo-400",
    },
    fastapi: {
      label: "FastAPI Service",
      classes:
        "bg-emerald-950/60 text-emerald-300 border-emerald-800/60 hover:border-emerald-700/80",
      dot: "bg-emerald-400",
    },
    hybrid: {
      label: "Dual-Engine Hybrid",
      classes:
        "bg-purple-950/60 text-purple-300 border-purple-800/60 hover:border-purple-700/80",
      dot: "bg-purple-400",
    },
  };

  const config = configs[engine];
  const sizeClasses =
    size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-xs font-semibold";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border transition-colors ${sizeClasses} ${config.classes} ${className}`}
    >
      {showIcon && <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />}
      <span>{config.label}</span>
    </span>
  );
};
