interface LoadingSkeletonProps {
  count?: number;
}

function SkeletonBlock({ className }: { className?: string }) {
  return (
    <div
      className={`rounded-lg bg-[rgb(var(--skeleton))] animate-pulse ${className ?? ""}`}
    />
  );
}

export function LoadingSkeleton({ count = 3 }: LoadingSkeletonProps) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="overflow-hidden rounded-xl bg-[var(--color-card)] shadow-[var(--card-shadow)]"
        >
          <div className="p-4 md:p-5" style={{ paddingLeft: "21px" }}>
            {/* Source badge */}
            <SkeletonBlock className="mb-3 h-5 w-20 rounded-full" />

            {/* Title */}
            <SkeletonBlock className="mb-2 h-6 w-3/4" />
            <SkeletonBlock className="mb-1 h-6 w-1/2" />

            {/* Summary lines */}
            <div className="mt-3 space-y-2">
              <SkeletonBlock className="h-4 w-full" />
              <SkeletonBlock className="h-4 w-5/6" />
              <SkeletonBlock className="h-4 w-2/3" />
            </div>

            {/* Tags */}
            <div className="mt-3 flex gap-1.5">
              <SkeletonBlock className="h-5 w-14 rounded-md" />
              <SkeletonBlock className="h-5 w-20 rounded-md" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
