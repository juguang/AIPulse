import { useState, useCallback } from "react";
import { ImageOff } from "lucide-react";

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
      <div className="relative flex aspect-video items-center justify-center rounded-lg bg-[rgb(var(--bg-tertiary))]">
        <ImageOff className="h-6 w-6 text-[rgb(var(--text-tertiary))]" />
      </div>
    );
  }

  return (
    <div className="relative aspect-video overflow-hidden rounded-lg">
      {status === "loading" && (
        <div className="absolute inset-0 bg-[rgb(var(--skeleton))] animate-pulse rounded-lg" />
      )}
      <img
        src={proxyUrl}
        alt={alt}
        onLoad={handleLoad}
        onError={handleError}
        className={`h-full w-full rounded-lg object-cover transition-all duration-300 ${
          status === "loaded" ? "opacity-100" : "opacity-0"
        }`}
      />
    </div>
  );
}
