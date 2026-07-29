import { useQuery } from "@tanstack/react-query";
import apiClient from "@/services/api";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const { data } = await apiClient.get("/health");
      return data;
    },
  });
}
