import { useQuery } from "@tanstack/react-query";
import { useFeedStore } from "@/stores/feed-store";
import type { FeedItem, PaginatedResponse } from "@/types/items";

const PAGE_SIZE = 20;

export function useItems() {
  const searchQuery = useFeedStore((s) => s.searchQuery);
  const activeCategory = useFeedStore((s) => s.activeCategory);
  const currentPage = useFeedStore((s) => s.currentPage);

  return useQuery<PaginatedResponse<FeedItem>>({
    queryKey: ["items", currentPage, activeCategory, searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: String(currentPage),
        page_size: String(PAGE_SIZE),
      });
      if (activeCategory && activeCategory !== "全部") {
        params.set("category", activeCategory);
      }
      if (searchQuery) {
        params.set("search", searchQuery);
      }
      const res = await fetch(`/api/v1/items?${params.toString()}`);
      if (!res.ok) throw new Error("获取内容失败");
      return res.json();
    },
    placeholderData: (prev) => prev,
  });
}
