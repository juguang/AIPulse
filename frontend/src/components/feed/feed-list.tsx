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

  // Priority 1: Loading (first load only — refetches keep existing data)
  if (isLoading) {
    return <LoadingSkeleton count={5} />;
  }

  // Priority 2: Error
  if (error) {
    return <ErrorState onRetry={onRetry} />;
  }

  // Priority 3: Empty state
  if (items.length === 0) {
    return <EmptyState type={searchQuery ? "search" : "feed"} />;
  }

  // Priority 4: Data
  return (
    <div className="flex flex-col gap-4">
      {items.map((item) => (
        <NewsCard key={item.id} item={item} />
      ))}
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={onPageChange}
      />
    </div>
  );
}
