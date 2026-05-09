import type { FeedItem } from "@/types/items";
import { NewsCard } from "@/components/feed/news-card";
import { Pagination } from "@/components/feed/pagination";
import { LoadingSkeleton } from "@/components/state/loading-skeleton";
import { EmptyState } from "@/components/state/empty-state";
import { ErrorState } from "@/components/state/error-state";
import { useFeedStore } from "@/stores/feed-store";

interface FeedListProps {
  items: FeedItem[];
  totalPages: number;
  isLoading: boolean;
  error: Error | null;
  onRetry: () => void;
  currentPage: number;
  onPageChange: (page: number) => void;
}

function formatDateLabel(date: Date, today: Date): string {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  const t = new Date(today);
  t.setHours(0, 0, 0, 0);
  const diff = (t.getTime() - d.getTime()) / 86400000;
  if (diff === 0) return "今天";
  if (diff === 1) return "昨天";
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}年${m}月${day}日`;
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function groupByDate(items: FeedItem[]): Map<string, FeedItem[]> {
  const groups = new Map<string, FeedItem[]>();
  for (const item of items) {
    const d = new Date(item.published_at);
    const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(item);
  }
  return groups;
}

function TimelineItem({ item, index }: { item: FeedItem; index: number }) {
  return (
    <div
      className="animate-stagger pl-5"
      style={{ animationDelay: `${index * 60}ms` }}
    >
      <div className="relative flex gap-4">
        {/* Timeline dot + time */}
        <div className="flex flex-col items-center">
          <div className="relative flex items-center justify-center">
            <div className="h-2 w-2 rounded-full bg-[rgb(var(--timeline-dot))] ring-4 ring-[rgb(var(--bg-primary))] group-hover:animate-pulse-dot-strong transition-all duration-200" />
          </div>
          <time className="mt-1.5 whitespace-nowrap text-[11px] tabular-nums tracking-tight text-[rgb(var(--text-tertiary))]">
            {formatTime(item.published_at)}
          </time>
        </div>

        {/* Card */}
        <div className="flex-1 pb-5 min-w-0">
          <NewsCard item={item} index={index} />
        </div>
      </div>
    </div>
  );
}

export function FeedList({
  items,
  totalPages,
  isLoading,
  error,
  onRetry,
  currentPage,
  onPageChange,
}: FeedListProps) {
  const searchQuery = useFeedStore((s) => s.searchQuery);

  if (isLoading) {
    return <LoadingSkeleton count={6} />;
  }

  if (error) {
    return <ErrorState onRetry={onRetry} />;
  }

  if (items.length === 0) {
    return <EmptyState type={searchQuery ? "search" : "feed"} />;
  }

  const today = new Date();
  const groups = groupByDate(items);

  return (
    <div className="space-y-1">
      {Array.from(groups.entries()).map(([dateKey, dateItems]) => (
        <div key={dateKey}>
          {/* Date section header with horizontal rule */}
          <div className="relative flex items-center gap-3 py-3">
            <div className="h-1 w-1 rounded-full bg-[rgb(var(--accent))] flex-shrink-0" />
            <span className="text-xs font-medium uppercase tracking-[0.15em] text-[rgb(var(--text-tertiary))]">
              {dateItems[0] ? formatDateLabel(new Date(dateItems[0].published_at), today) : dateKey}
            </span>
            <div className="flex-1 h-px bg-[rgb(var(--border-light))]" />
          </div>

          {/* Items */}
          {dateItems.map((item, idx) => (
            <TimelineItem
              key={item.id}
              item={item}
              index={idx}
            />
          ))}
        </div>
      ))}

      <div className="pt-2">
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={onPageChange}
        />
      </div>
    </div>
  );
}
