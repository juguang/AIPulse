import { useFeedStore } from "@/stores/feed-store";
import { useItems } from "@/hooks/use-items";
import { SearchBar } from "@/components/feed/search-bar";
import { CategoryTabs } from "@/components/feed/category-tabs";
import { FeedList } from "@/components/feed/feed-list";

function App() {
  const { data: itemsData, error, refetch, isPending } = useItems();
  const currentPage = useFeedStore((s) => s.currentPage);
  const setCurrentPage = useFeedStore((s) => s.setCurrentPage);

  return (
    <div className="min-h-screen bg-background">
      {/* Sticky header with brand + search */}
      <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex max-w-[960px] items-center justify-between gap-4 px-4 py-3">
          <h1 className="text-lg font-semibold whitespace-nowrap">AI Pulse</h1>
          <div className="w-full max-w-[400px]">
            <SearchBar />
          </div>
        </div>
      </header>

      {/* Main content area */}
      <main className="mx-auto max-w-[960px] px-4 py-4">
        <CategoryTabs />

        <div className="mt-4">
          <FeedList
            items={itemsData?.items ?? []}
            totalPages={itemsData?.total_pages ?? 1}
            isLoading={isPending}
            error={error}
            onRetry={refetch}
            currentPage={currentPage}
            onPageChange={setCurrentPage}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
