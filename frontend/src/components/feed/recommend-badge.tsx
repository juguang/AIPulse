import { Star } from "lucide-react";

export function RecommendBadge({ score }: { score: number | null }) {
  if (score === null || score < 5) return null;

  const color =
    score >= 8
      ? "text-[rgb(var(--score-high))]"
      : "text-[rgb(var(--score-mid))]";

  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium ${color}`}>
      <Star className="h-3 w-3 fill-current" />
      {score.toFixed(1)}
    </span>
  );
}
