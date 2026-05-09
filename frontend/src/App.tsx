import { Sun, Moon } from "lucide-react";
import { useThemeStore } from "@/stores/theme-store";
import { useFeedStore } from "@/stores/feed-store";
import { useItems } from "@/hooks/use-items";
import { SearchBar } from "@/components/feed/search-bar";
import { CategoryTabs } from "@/components/feed/category-tabs";
import { FeedList } from "@/components/feed/feed-list";

function App() {
  const { data: itemsData, error, refetch, isPending } = useItems();
  const currentPage = useFeedStore((s) => s.currentPage);
  const setCurrentPage = useFeedStore((s) => s.setCurrentPage);
  const { theme, toggle } = useThemeStore();

  return (
    <div className="min-h-dvh">
      {/* Sticky header */}
      <header className="sticky top-0 z-10 bg-[var(--color-background)]/80 backdrop-blur-lg">
        <div className="mx-auto max-w-[960px] px-4 md:px-6">
          {/* Brand row */}
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center gap-3">
              <h1 className="font-serif text-2xl tracking-tight text-[rgb(var(--text-primary))]">
                AI Pulse
              </h1>
              <span className="h-2 w-2 rounded-full bg-[rgb(var(--accent))] animate-pulse-dot" />
            </div>

            <div className="flex items-center gap-2 md:gap-4">
              <div className="hidden sm:block">
                <SearchBar />
              </div>
              <button
                onClick={toggle}
                className="flex h-9 w-9 items-center justify-center rounded-full text-[rgb(var(--text-secondary))] hover:bg-[rgb(var(--bg-tertiary))] hover:text-[rgb(var(--text-primary))] transition-colors"
                aria-label={theme === "light" ? "切换深色模式" : "切换浅色模式"}
              >
                {theme === "light" ? (
                  <Moon className="h-4 w-4" />
                ) : (
                  <Sun className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>

          {/* Category tabs + mobile search */}
          <div className="flex items-center gap-3 pb-3">
            <div className="flex-1 min-w-0">
              <CategoryTabs />
            </div>
            <div className="sm:hidden flex-shrink-0">
              <SearchBar />
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-[960px] px-4 md:px-6 py-6 md:py-8">
        <FeedList
          items={itemsData?.items ?? []}
          totalPages={itemsData?.total_pages ?? 1}
          isLoading={isPending}
          error={error}
          onRetry={refetch}
          currentPage={currentPage}
          onPageChange={setCurrentPage}
        />
      </main>
    </div>
  );
}

export default App;
