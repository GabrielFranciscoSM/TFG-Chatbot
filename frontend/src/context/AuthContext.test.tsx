import { act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider, useAuth } from "@/context/AuthContext";

// Mock the api module
vi.mock("@/lib/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

import api from "@/lib/api";

const wrapper = ({ children }: { children: ReactNode }) => <AuthProvider>{children}</AuthProvider>;

describe("useAuth", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it("should throw error when used outside AuthProvider", () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    expect(() => {
      renderHook(() => useAuth());
    }).toThrow("useAuth must be used within an AuthProvider");

    consoleSpy.mockRestore();
  });

  it("should initialize as not authenticated when no token", async () => {
    vi.mocked(api.get).mockResolvedValue({ data: null });

    const { result } = renderHook(() => useAuth(), { wrapper });

    // Wait for initialization to complete
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Should be unauthenticated with no user
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
  });

  it("should login successfully", async () => {
    vi.mocked(api.get).mockResolvedValue({ data: null });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const mockUser = {
      username: "testuser",
      email: "test@example.com",
      role: "student",
      subjects: ["iv"],
    };

    act(() => {
      result.current.login("test-token", mockUser);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.token).toBe("test-token");
    expect(localStorage.setItem).toHaveBeenCalledWith("token", "test-token");
  });

  it("should logout successfully", async () => {
    vi.mocked(api.get).mockResolvedValue({ data: null });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // First login
    const mockUser = {
      username: "testuser",
      email: "test@example.com",
      role: "student",
      subjects: [],
    };

    act(() => {
      result.current.login("test-token", mockUser);
    });

    expect(result.current.isAuthenticated).toBe(true);

    // Then logout
    act(() => {
      result.current.logout();
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(localStorage.removeItem).toHaveBeenCalledWith("token");
  });

  it("should restore session from localStorage on mount", async () => {
    const mockUser = {
      username: "testuser",
      email: "test@example.com",
      role: "professor",
      subjects: ["iv", "tfg"],
    };

    // Mock localStorage to return a token
    vi.mocked(localStorage.getItem).mockReturnValue("stored-token");
    vi.mocked(api.get).mockResolvedValue({ data: mockUser });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual(mockUser);
  });

  it("should logout if token verification fails", async () => {
    vi.mocked(localStorage.getItem).mockReturnValue("invalid-token");
    vi.mocked(api.get).mockRejectedValue(new Error("Unauthorized"));

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });
});
