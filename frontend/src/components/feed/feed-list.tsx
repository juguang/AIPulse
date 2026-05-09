import { useFeedStore } from "@/stores/feed-store";
import type { FeedItem } from "@/types/items";
import { NewsCard } from "@/components/feed/news-card";
import { Pagination } from "@/components/feed/pagination";
import { LoadingSkeleton } from "@/components/state/loading-skeleton";
import { EmptyState } from "@/components/state/empty-state";
import { ErrorState } from "@/components/state/error-state";

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

function TimelineItem({ item, isLast }: { item: FeedItem; isLast: boolean }) {
  return (
    <div className="relative flex gap-4">
      {/* Left: timeline dot + time */}
      <div className="flex flex-col items-center">
        {/* Vertical line above dot */}
        <div className="w-px bg-border min-h-[12px]" />
        {/* Dot */}
        <div className="w-2 h-2 rounded-full bg-primary/30 flex-shrink-0" />
        {/* Time below dot */}
        <time className="text-[11px] text-muted-foreground tabular-nums mt-1.5 whitespace-nowrap">
          {formatTime(item.published_at)}
        </time>
        {/* Vertical line below (extends to next item) */}
        {!isLast && <div className="w-px bg-border flex-1 mt-1.5" />}
      </div>

      {/* Right: card */}
      <div className="flex-1 pb-6">
        <NewsCard item={item} />
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
    return <LoadingSkeleton count={5} />;
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
    <div className="flex flex-col">
      {Array.from(groups.entries()).map(([dateKey, dateItems]) => (
        <div key={dateKey}>
          {/* Date header with timeline dot */}
          <div className="relative flex items-center gap-4 pl-[5px]">
            <div className="w-3 h-3 rounded-full border-2 border-primary bg-background flex-shrink-0 z-10" />
            <span className="text-sm font-medium text-foreground">
              {formatDateLabel(new Date(dateItems[0].published_at), today)}
            </span>
          </div>

          {/* Timeline line from date header dot down */}
          <div className="ml-[17px] border-l border-border">
            {dateItems.map((item, idx) => (
              <TimelineItem
                key={item.id}
                item={item}
                isLast={idx === dateItems.length - 1}
              />
            ))}
          </div>
        </div>
      ))}

      <div className="mt-4">
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={onPageChange}
        />
      </div>
    </div>
  );
}
