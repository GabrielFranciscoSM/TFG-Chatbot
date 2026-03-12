// User preferences types

export interface UserPreferences {
  default_test_questions: number;
  default_test_difficulty: "easy" | "medium" | "hard";
}

export const DEFAULT_PREFERENCES: UserPreferences = {
  default_test_questions: 5,
  default_test_difficulty: "medium",
};
