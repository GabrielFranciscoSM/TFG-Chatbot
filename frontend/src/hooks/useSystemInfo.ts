import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export interface SystemInfo {
  version: string;
  llm_provider: string;
  llm_model: string;
  status: "operational" | "unavailable";
}

const DEFAULT_SYSTEM_INFO: SystemInfo = {
  version: "unknown",
  llm_provider: "Unknown",
  llm_model: "Unknown",
  status: "unavailable",
};

/**
 * Hook to fetch system information
 */
export function useSystemInfo() {
  return useQuery<SystemInfo>({
    queryKey: ["system", "info"],
    queryFn: async () => {
      const response = await api.get("/system/info");
      return response.data;
    },
    placeholderData: DEFAULT_SYSTEM_INFO,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    retry: 1,
  });
}
