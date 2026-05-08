import { useState, useCallback } from "react";
import { ImageOff } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface ImageProxyProps {
  src: string | null;
  alt?: string;
}

export function ImageProxy({ src, alt = "" }: ImageProxyProps) {
  const [status, setStatus] = useState<"loading" | "loaded" | "error">(
    "loading",
  );

  const handleLoad = useCallback(() => {
    setStatus("loaded");
  }, []);

  const handleError = useCallback(() => {
    setStatus("error");
  }, []);

  if (!src) return null;

  const proxyUrl = `/api/images/proxy?url=${encodeURIComponent(src)}`;

  if (status === "error") {
    return (
      <div className="relative aspect-video rounded-lg bg-muted flex items-center justify-center">
        <ImageOff className="w-8 h-8 text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="relative aspect-video rounded-lg overflow-hidden">
      {status === "loading" && (
        <Skeleton className="absolute inset-0 rounded-lg" />
      )}
      <img
        src={proxyUrl}
        alt={alt}
        onLoad={handleLoad}
        onError={handleError}
        className={cn(
          "w-full h-full object-cover rounded-lg transition-transform duration-200",
          status === "loaded" && "hover:scale-[1.02]",
          status === "loading" && "opacity-0",
        )}
      />
    </div>
  );
}
