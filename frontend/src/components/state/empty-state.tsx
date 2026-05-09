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
    <div className="flex flex-col items-center justify-center gap-4 py-20">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[rgb(var(--bg-tertiary))]">
        <Icon className="h-6 w-6 text-[rgb(var(--text-tertiary))]" />
      </div>
      <h2 className="font-serif text-xl text-[rgb(var(--text-primary))]">
        {heading}
      </h2>
      <p className="max-w-xs text-center text-sm leading-relaxed text-[rgb(var(--text-secondary))]">
        {body}
      </p>
    </div>
  );
}
