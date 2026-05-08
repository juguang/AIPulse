import { useMemo } from "react";

interface RelativeTimeProps {
  datetime: string;
}

function getRelativeTime(isoString: string): string {
  const now = Date.now();
  const then = new Date(isoString).getTime();
  const diffMs = now - then;

  if (diffMs < 0) return "刚刚";

  const diffMinutes = Math.floor(diffMs / 60000);

  if (diffMinutes < 1) return "刚刚";
  if (diffMinutes < 60) return `${diffMinutes} 分钟前`;

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours} 小时前`;

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} 天前`;
}

export function RelativeTime({ datetime }: RelativeTimeProps) {
  const text = useMemo(() => getRelativeTime(datetime), [datetime]);
  return <span className="text-sm text-muted-foreground">{text}</span>;
}
