import { useQuery } from "@tanstack/react-query";
import type { Category } from "@/types/items";

export function useCategories() {
  return useQuery<Category[]>({
    queryKey: ["categories"],
    queryFn: async () => {
      const res = await fetch("/api/v1/categories");
      if (!res.ok) throw new Error("获取分类失败");
      return res.json();
    },
    staleTime: 30 * 60 * 1000,
  });
}
