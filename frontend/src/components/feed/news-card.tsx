import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { SourceBadge } from "@/components/feed/source-badge";
import { ImageProxy } from "@/components/feed/image-proxy";
import { TagChip } from "@/components/feed/tag-chip";
import { RecommendBadge } from "@/components/feed/recommend-badge";
import type { FeedItem } from "@/types/items";

interface NewsCardProps {
  item: FeedItem;
}

export function NewsCard({ item }: NewsCardProps) {
  return (
    <a
      href={item.source_url}
      target="_blank"
      rel="noopener noreferrer"
      className="block"
    >
      <Card className="hover:shadow-md hover:border-accent cursor-pointer transition-all duration-200">
        <CardContent className="p-4 space-y-3">
          {/* Row 1: SourceBadge */}
          <div className="flex justify-between items-center">
            <SourceBadge name={item.source_name} />
          </div>

          <Separator />

          {/* Image (if present) */}
          {item.image_url && (
            <ImageProxy src={item.image_url} alt={item.title} />
          )}

          {/* Title */}
          <h3 className="text-lg font-semibold leading-tight line-clamp-2">
            {item.title}
          </h3>

          {/* Summary */}
          {item.summary && (
            <p className="text-base leading-normal line-clamp-3 text-muted-foreground">
              {item.summary}
            </p>
          )}

          {/* Row: Tags + RecommendBadge */}
          <div className="flex items-center justify-between gap-2">
            {item.tags && item.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {item.tags.map((tag) => (
                  <TagChip key={tag} label={tag} />
                ))}
              </div>
            )}
            <div className="ml-auto">
              <RecommendBadge score={item.recommended_score} />
            </div>
          </div>
        </CardContent>
      </Card>
    </a>
  );
}
