import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface HealthResponse {
  status: string;
  version: string;
  database: string;
}

function App() {
  const {
    data: health,
    isLoading,
    error,
    refetch,
  } = useQuery<HealthResponse>({
    queryKey: ["health"],
    queryFn: async () => {
      const res = await fetch("/health");
      if (!res.ok) throw new Error("API 不可用");
      return res.json();
    },
  });

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">
            AI Pulse
          </CardTitle>
          <CardDescription className="text-center">
            AI 资讯精选聚合平台
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-3 rounded-lg bg-neutral-100">
            <span className="text-sm font-medium">API 状态</span>
            <span
              className={`text-sm px-2 py-0.5 rounded-full ${
                isLoading
                  ? "bg-yellow-100 text-yellow-700"
                  : error
                    ? "bg-red-100 text-red-700"
                    : "bg-green-100 text-green-700"
              }`}
            >
              {isLoading
                ? "连接中..."
                : error
                  ? "未连接"
                  : "已连接"}
            </span>
          </div>

          {health && (
            <>
              <div className="flex items-center justify-between p-3 rounded-lg bg-neutral-100">
                <span className="text-sm font-medium">API 版本</span>
                <span className="text-sm text-neutral-600">
                  {health.version}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-neutral-100">
                <span className="text-sm font-medium">数据库</span>
                <span
                  className={`text-sm px-2 py-0.5 rounded-full ${
                    health.database === "connected"
                      ? "bg-green-100 text-green-700"
                      : "bg-yellow-100 text-yellow-700"
                  }`}
                >
                  {health.database === "connected"
                    ? "已连接"
                    : "未连接"}
                </span>
              </div>
            </>
          )}

          <Button
            className="w-full"
            variant="outline"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            {isLoading ? "刷新中..." : "刷新状态"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

export default App;
