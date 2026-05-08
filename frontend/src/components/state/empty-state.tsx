import { FileText, SearchX } from "lucide-react";

interface EmptyStateProps {
  type: "feed" | "search";
}

const config = {
  feed: {
    Icon: FileText,
    heading: "暂无内容",
    body: "信息流还没准备好，请稍后再来",
  },
  search: {
    Icon: SearchX,
    heading: "未找到相关内容",
    body: "试试其他关键词或调整筛选分类",
  },
} as const;

export function EmptyState({ type }: EmptyStateProps) {
  const { Icon, heading, body } = config[type];

  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16">
      <Icon className="w-12 h-12 text-muted-foreground" />
      <h2 className="text-2xl font-semibold">{heading}</h2>
      <p className="text-muted-foreground text-center max-w-sm">{body}</p>
    </div>
  );
}
