import { Badge } from "@/components/ui/badge";

interface RecommendBadgeProps {
  score: number | null;
}

export function RecommendBadge({ score }: RecommendBadgeProps) {
  if (score === null || score < 5) return null;

  const colorClass =
    score >= 8
      ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100"
      : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100";

  return (
    <Badge className={colorClass}>
      AI 推荐 {score.toFixed(1)}
    </Badge>
  );
}
