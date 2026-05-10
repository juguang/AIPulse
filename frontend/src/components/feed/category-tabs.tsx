import { useCategories } from "@/hooks/use-categories";
import { useFeedStore } from "@/stores/feed-store";

const DEFAULT_CATEGORIES = ["全部", "模型", "产品", "行业", "研究", "工程"];

export function CategoryTabs() {
  const activeCategory = useFeedStore((s) => s.activeCategory);
  const setActiveCategory = useFeedStore((s) => s.setActiveCategory);
  const { data: apiCategories } = useCategories();
  const categories =
    apiCategories && apiCategories.length > 0
      ? apiCategories
      : DEFAULT_CATEGORIES;

  return (
    <div className="overflow-x-auto scrollbar-hide">
      <div className="flex gap-1.5">
        {categories.map((cat) => {
          const isActive = cat === activeCategory;
          return (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`
                relative whitespace-nowrap rounded-full px-3.5 py-1.5 text-xs font-medium
                transition-all duration-200
                ${
                  isActive
                    ? "bg-[rgb(var(--accent))] text-white shadow-sm"
                    : "bg-[rgb(var(--bg-tertiary))] text-[rgb(var(--text-secondary))] hover:bg-[rgb(var(--border))] hover:text-[rgb(var(--text-primary))]"
                }
              `}
            >
              {cat}
            </button>
          );
        })}
      </div>
    </div>
  );
}
