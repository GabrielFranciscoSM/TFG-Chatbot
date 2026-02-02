import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import type { UserPreferences } from "@/types/preferences";
import { DEFAULT_PREFERENCES } from "@/types/preferences";

/**
 * Hook to fetch user preferences
 */
export function useUserPreferences() {
  return useQuery<UserPreferences>({
    queryKey: ["user", "preferences"],
    queryFn: async () => {
      const response = await api.get("/users/me/preferences");
      return response.data;
    },
    // Return defaults if the query fails (e.g., old users without preferences)
    placeholderData: DEFAULT_PREFERENCES,
  });
}

/**
 * Hook to update user preferences
 */
export function useUpdatePreferences() {
  const queryClient = useQueryClient();

  return useMutation<UserPreferences, Error, UserPreferences>({
    mutationFn: async (preferences: UserPreferences) => {
      const response = await api.put("/users/me/preferences", preferences);
      return response.data;
    },
    onSuccess: (data) => {
      // Update the cache with new preferences
      queryClient.setQueryData(["user", "preferences"], data);
    },
  });
}
