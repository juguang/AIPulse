import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useCategories } from "@/hooks/use-categories";
import { useFeedStore } from "@/stores/feed-store";

const DEFAULT_CATEGORIES = ["全部", "模型", "产品", "行业", "论文", "技巧"];

export function CategoryTabs() {
  const activeCategory = useFeedStore((s) => s.activeCategory);
  const setActiveCategory = useFeedStore((s) => s.setActiveCategory);
  const { data: apiCategories } = useCategories();
  const categories = apiCategories && apiCategories.length > 0 ? apiCategories : DEFAULT_CATEGORIES;

  return (
    <div className="overflow-x-auto scrollbar-hide">
      <Tabs
        value={activeCategory}
        onValueChange={setActiveCategory}
        className="w-full"
      >
        <TabsList className="w-full justify-start h-auto gap-0 rounded-none bg-transparent border-b p-0">
          {categories.map((cat) => (
            <TabsTrigger
              key={cat}
              value={cat}
              className="relative px-4 py-3 text-sm font-medium rounded-none bg-transparent
                         data-[state=active]:bg-transparent data-[state=active]:text-primary
                         data-[state=active]:font-semibold data-[state=active]:shadow-none
                         data-[state=inactive]:text-muted-foreground
                         after:absolute after:bottom-0 after:left-0 after:right-0
                         after:h-0.5 after:bg-primary
                         data-[state=inactive]:after:opacity-0 data-[state=active]:after:opacity-100
                         after:transition-opacity
                         hover:text-foreground hover:after:opacity-50
                         transition-colors whitespace-nowrap"
            >
              {cat}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>
    </div>
  );
}
