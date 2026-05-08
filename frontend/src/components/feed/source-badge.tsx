import { Badge } from "@/components/ui/badge";

interface SourceBadgeProps {
  name: string;
}

export function SourceBadge({ name }: SourceBadgeProps) {
  return <Badge variant="outline">来源: {name}</Badge>;
}
