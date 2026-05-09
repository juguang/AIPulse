import { useState, useEffect, useRef } from "react";
import { Search, X } from "lucide-react";
import { useFeedStore } from "@/stores/feed-store";

export function SearchBar() {
  const searchQuery = useFeedStore((s) => s.searchQuery);
  const setSearchQuery = useFeedStore((s) => s.setSearchQuery);
  const [localValue, setLocalValue] = useState(searchQuery);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setLocalValue(searchQuery);
  }, [searchQuery]);

  const debouncedSet = (value: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setSearchQuery(value);
    }, 300);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setLocalValue(newValue);
    debouncedSet(newValue);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      setSearchQuery(localValue);
    }
  };

  const handleClear = () => {
    setLocalValue("");
    if (debounceRef.current) clearTimeout(debounceRef.current);
    setSearchQuery("");
  };

  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[rgb(var(--text-tertiary))]" />
      <input
        className="h-8 w-[160px] rounded-full border border-[rgb(var(--border))] bg-[rgb(var(--bg-secondary))] pl-8 pr-7 text-xs text-[rgb(var(--text-primary))] placeholder:text-[rgb(var(--text-tertiary))] outline-none focus:border-[rgb(var(--accent))] focus:ring-1 focus:ring-[rgb(var(--accent))] transition-all duration-200"
        placeholder="搜索..."
        value={localValue}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
      />
      {localValue && (
        <button
          type="button"
          onClick={handleClear}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-[rgb(var(--text-tertiary))] hover:text-[rgb(var(--text-primary))] transition-colors"
          aria-label="清除搜索"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}
