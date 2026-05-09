import { AlertCircle, RotateCcw } from "lucide-react";

interface ErrorStateProps {
  onRetry: () => void;
}

export function ErrorState({ onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-20">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-50 dark:bg-red-950/30">
        <AlertCircle className="h-6 w-6 text-red-500" />
      </div>
      <h2 className="font-serif text-xl text-[rgb(var(--text-primary))]">
        加载失败
      </h2>
      <p className="max-w-xs text-center text-sm leading-relaxed text-[rgb(var(--text-secondary))]">
        无法获取内容，请检查网络连接后重试
      </p>
      <button
        onClick={onRetry}
        className="inline-flex items-center gap-1.5 rounded-full bg-[rgb(var(--accent))] px-4 py-2 text-xs font-medium text-white transition-all duration-200 hover:brightness-110 active:scale-95"
      >
        <RotateCcw className="h-3.5 w-3.5" />
        重新加载
      </button>
    </div>
  );
}
