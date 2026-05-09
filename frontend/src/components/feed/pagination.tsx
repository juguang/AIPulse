import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

function getPageNumbers(current: number, total: number): (number | "ellipsis")[] {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const pages: (number | "ellipsis")[] = [1];

  const windowStart = Math.max(2, current - 2);
  const windowEnd = Math.min(total - 1, current + 2);

  if (windowStart > 2) {
    pages.push("ellipsis");
  }

  for (let i = windowStart; i <= windowEnd; i++) {
    pages.push(i);
  }

  if (windowEnd < total - 1) {
    pages.push("ellipsis");
  }

  pages.push(total);

  return pages;
}

export function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;

  const isFirstPage = currentPage <= 1;
  const isLastPage = currentPage >= totalPages;
  const pageNumbers = getPageNumbers(currentPage, totalPages);

  const baseBtn =
    "inline-flex items-center justify-center rounded-lg text-sm font-medium transition-all duration-200";
  const activeBtn =
    "bg-[rgb(var(--accent))] text-white";
  const inactiveBtn =
    "text-[rgb(var(--text-secondary))] hover:bg-[rgb(var(--bg-tertiary))] hover:text-[rgb(var(--text-primary))]";
  const disabledBtn =
    "text-[rgb(var(--text-tertiary))] opacity-40 cursor-not-allowed";

  return (
    <nav className="flex items-center justify-center gap-1 py-4" aria-label="分页导航">
      {/* Mobile: simplified */}
      <div className="flex md:hidden items-center gap-2">
        <button
          className={`${baseBtn} h-8 w-8 ${isFirstPage ? disabledBtn : inactiveBtn}`}
          disabled={isFirstPage}
          onClick={() => onPageChange(currentPage - 1)}
          aria-label="上一页"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <span className="text-xs text-[rgb(var(--text-tertiary))] whitespace-nowrap">
          {currentPage} / {totalPages}
        </span>
        <button
          className={`${baseBtn} h-8 w-8 ${isLastPage ? disabledBtn : inactiveBtn}`}
          disabled={isLastPage}
          onClick={() => onPageChange(currentPage + 1)}
          aria-label="下一页"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>

      {/* Desktop */}
      <div className="hidden md:flex items-center gap-1">
        <button
          className={`${baseBtn} h-8 w-8 ${isFirstPage ? disabledBtn : inactiveBtn}`}
          disabled={isFirstPage}
          onClick={() => onPageChange(currentPage - 1)}
          aria-label="上一页"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>

        {pageNumbers.map((page, index) => {
          if (page === "ellipsis") {
            return (
              <span
                key={`ellipsis-${index}`}
                className="flex h-8 w-8 items-center justify-center text-xs text-[rgb(var(--text-tertiary))]"
              >
                ...
              </span>
            );
          }

          return (
            <button
              key={page}
              className={`${baseBtn} h-8 min-w-[32px] px-2 ${
                page === currentPage ? activeBtn : inactiveBtn
              }`}
              onClick={() => onPageChange(page)}
            >
              {page}
            </button>
          );
        })}

        <button
          className={`${baseBtn} h-8 w-8 ${isLastPage ? disabledBtn : inactiveBtn}`}
          disabled={isLastPage}
          onClick={() => onPageChange(currentPage + 1)}
          aria-label="下一页"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </nav>
  );
}
