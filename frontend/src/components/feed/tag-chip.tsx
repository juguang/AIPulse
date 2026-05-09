export function TagChip({ label }: { label: string }) {
  return (
    <span className="inline-block rounded-md border border-[rgb(var(--border-light))] bg-[rgb(var(--bg-tertiary))] px-2 py-0.5 text-[11px] font-medium text-[rgb(var(--text-secondary))]">
      {label}
    </span>
  );
}
