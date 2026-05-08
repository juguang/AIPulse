import { create } from "zustand";

interface FeedState {
  searchQuery: string;
  activeCategory: string;
  currentPage: number;
  setSearchQuery: (q: string) => void;
  setActiveCategory: (c: string) => void;
  setCurrentPage: (p: number) => void;
}

/**
 * 从 URL search params 初始化 store（支持分享链接直接恢复状态）
 * 使用 History API 在状态变更时同步 URL，不触发页面重载
 */
function getInitialParams() {
  const params = new URLSearchParams(window.location.search);
  return {
    searchQuery: params.get("search") || "",
    activeCategory: params.get("category") || "全部",
    currentPage: Math.max(1, parseInt(params.get("page") || "1", 10) || 1),
  };
}

function syncUrl(state: Partial<FeedState>) {
  const params = new URLSearchParams(window.location.search);
  if (state.searchQuery !== undefined) {
    state.searchQuery ? params.set("search", state.searchQuery) : params.delete("search");
  }
  if (state.activeCategory !== undefined && state.activeCategory !== "全部") {
    params.set("category", state.activeCategory);
  } else {
    params.delete("category");
  }
  if (state.currentPage !== undefined && state.currentPage > 1) {
    params.set("page", String(state.currentPage));
  } else {
    params.delete("page");
  }
  const newUrl = params.toString() ? `?${params.toString()}` : window.location.pathname;
  window.history.replaceState(null, "", newUrl);
}

export const useFeedStore = create<FeedState>((set) => ({
  ...getInitialParams(),
  setSearchQuery: (q) =>
    set(() => {
      syncUrl({ searchQuery: q });
      return { searchQuery: q, currentPage: 1 };
    }),
  setActiveCategory: (c) =>
    set(() => {
      syncUrl({ activeCategory: c });
      return { activeCategory: c, currentPage: 1 };
    }),
  setCurrentPage: (p) =>
    set(() => {
      syncUrl({ currentPage: p });
      return { currentPage: p };
    }),
}));
