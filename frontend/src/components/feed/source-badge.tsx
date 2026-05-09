export function SourceBadge({ name }: { name: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-[rgb(var(--accent-light))] px-2.5 py-0.5 text-[11px] font-medium text-[rgb(var(--accent))]">
      <span className="h-1 w-1 rounded-full bg-current opacity-60" />
      {name}
    </span>
  );
}
