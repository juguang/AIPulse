import { Badge } from "@/components/ui/badge";

interface TagChipProps {
  label: string;
}

export function TagChip({ label }: TagChipProps) {
  return <Badge variant="secondary">{label}</Badge>;
}
