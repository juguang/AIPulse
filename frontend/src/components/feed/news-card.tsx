import { SourceBadge } from "@/components/feed/source-badge";
import { ImageProxy } from "@/components/feed/image-proxy";
import { TagChip } from "@/components/feed/tag-chip";
import { RecommendBadge } from "@/components/feed/recommend-badge";
import type { FeedItem } from "@/types/items";

interface NewsCardProps {
  item: FeedItem;
  index: number;
}

export function NewsCard({ item, index }: NewsCardProps) {
  return (
    <a
      href={item.source_url}
      target="_blank"
      rel="noopener noreferrer"
      className="group relative block rounded-xl bg-[var(--color-card)] text-[var(--color-card-foreground)] shadow-[var(--card-shadow)] hover:shadow-[var(--card-shadow-hover)] transition-all duration-200"
      style={{ animationDelay: `${index * 60}ms` }}
    >
      {/* Left accent bar on hover */}
      <span className="absolute left-0 top-2 bottom-2 w-0.5 rounded-r-full bg-[rgb(var(--accent))] scale-y-0 group-hover:scale-y-100 transition-transform duration-200 origin-top" />

      <div className="p-4 md:p-5 pl-[17px] md:pl-[21px]">
        {/* Source row */}
        <div className="mb-2.5">
          <SourceBadge name={item.source_name} />
        </div>

        {/* Image */}
        {item.image_url && (
          <div className="mb-3">
            <ImageProxy src={item.image_url} alt={item.title} />
          </div>
        )}

        {/* Title */}
        <h3 className="font-serif text-lg md:text-xl leading-snug text-[rgb(var(--text-primary))] line-clamp-2 group-hover:text-[rgb(var(--accent))] transition-colors duration-200">
          {item.title}
        </h3>

        {/* Summary */}
        {item.summary && (
          <p className="mt-2 text-sm md:text-base leading-relaxed text-[rgb(var(--text-secondary))] line-clamp-3">
            {item.summary}
          </p>
        )}

        {/* Footer: Tags + Score */}
        <div className="mt-3 flex items-center justify-between gap-2">
          {item.tags && item.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {item.tags.map((tag) => (
                <TagChip key={tag} label={tag} />
              ))}
            </div>
          )}
          <div className="ml-auto flex-shrink-0">
            <RecommendBadge score={item.recommended_score} />
          </div>
        </div>
      </div>
    </a>
  );
}
