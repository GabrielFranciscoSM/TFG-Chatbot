import type { AxiosError } from "axios";

interface ApiErrorResponse {
  detail?: string;
  message?: string;
}

export type ApiError = AxiosError<ApiErrorResponse>;

export function getErrorMessage(error: unknown, fallback: string): string {
  if (isApiError(error)) {
    return error.response?.data?.detail || error.response?.data?.message || fallback;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return fallback;
}

function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === "object" &&
    error !== null &&
    "response" in error &&
    typeof (error as ApiError).response === "object"
  );
}
