import React from "react";
import { cn } from "../../lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "positive" | "negative" | "neutral";
  className?: string;
}

export function Badge({ children, variant = "default", className }: BadgeProps) {
  const variants = {
    default: "bg-gray-100 text-gray-800",
    positive: "bg-green-100 text-green-800",
    negative: "bg-red-100 text-red-800",
    neutral: "bg-blue-100 text-blue-800",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

export function SentimentBadge({ sentiment }: { sentiment: string | null }) {
  if (!sentiment) return null;

  const config = {
    positive: { label: "Positivo", variant: "positive" as const },
    negative: { label: "Negativo", variant: "negative" as const },
    neutral: { label: "Neutro", variant: "neutral" as const },
  };

  const { label, variant } = config[sentiment as keyof typeof config] || {
    label: sentiment,
    variant: "default" as const,
  };

  return <Badge variant={variant}>{label}</Badge>;
}
