import { AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorStateProps {
  onRetry: () => void;
}

export function ErrorState({ onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16">
      <AlertCircle className="w-12 h-12 text-destructive" />
      <h2 className="text-2xl font-semibold">加载失败</h2>
      <p className="text-muted-foreground text-center max-w-sm">
        无法获取内容，请检查网络连接后重试
      </p>
      <Button variant="outline" onClick={onRetry}>
        重新加载
      </Button>
    </div>
  );
}
