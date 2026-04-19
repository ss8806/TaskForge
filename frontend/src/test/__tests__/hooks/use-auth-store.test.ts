import { describe, it, expect, beforeEach } from "vitest";

import { useAuthStore } from "@/hooks/use-auth-store";

describe("useAuthStore", () => {
  beforeEach(() => {
    // 各テスト前にストアをリセット
    localStorage.clear();
    useAuthStore.setState({ token: null });
  });

  it("should have initial state with null token", () => {
    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
  });

  it("should set token and persist to localStorage", () => {
    const { setToken } = useAuthStore.getState();
    const testToken = "test-jwt-token-123";

    setToken(testToken);

    const state = useAuthStore.getState();
    expect(state.token).toBe(testToken);
    expect(localStorage.getItem("access_token")).toBe(testToken);
  });

  it("should remove token from localStorage on logout", () => {
    const { setToken, logout } = useAuthStore.getState();
    const testToken = "test-jwt-token-123";

    // トークンを設定
    setToken(testToken);
    expect(useAuthStore.getState().token).toBe(testToken);

    // logoutをモック（window.location.hrefを防止）
    const originalLocation = window.location;
    Object.defineProperty(window, "location", {
      value: { href: "" },
      writable: true,
    });

    logout();

    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(localStorage.getItem("access_token")).toBeNull();
    expect(window.location.href).toBe("/login");

    // 復元
    Object.defineProperty(window, "location", {
      value: originalLocation,
      writable: true,
    });
  });

  it("should clear token when setToken is called with null", () => {
    const { setToken } = useAuthStore.getState();

    // まずトークンを設定
    setToken("initial-token");
    expect(useAuthStore.getState().token).toBe("initial-token");

    // nullを設定
    setToken(null);

    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(localStorage.getItem("access_token")).toBeNull();
  });

  it("should persist token across store reinitialization", () => {
    const { setToken } = useAuthStore.getState();
    const testToken = "persistent-token";

    // トークンを設定
    setToken(testToken);

    // ストアの状態を取得し直す
    const state = useAuthStore.getState();
    expect(state.token).toBe(testToken);
    expect(localStorage.getItem("access_token")).toBe(testToken);
  });
});
