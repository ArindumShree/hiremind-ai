import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import apiClient, { clearTokens, setTokens } from "../services/api";
import type { TokenPair, User } from "../types";
import { AuthContext, type AuthContextValue, type RegisterPayload } from "./authContextValue";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    async function loadUser() {
      const token = localStorage.getItem("hm_access_token");
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const { data } = await apiClient.get<User>("/auth/me");
        if (active) setUser(data);
      } catch {
        if (active) setUser(null);
      } finally {
        if (active) setLoading(false);
      }
    }
    void loadUser();
    return () => {
      active = false;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await apiClient.post<TokenPair>("/auth/login", {
      email,
      password,
    });
    setTokens(data);
    const me = await apiClient.get<User>("/auth/me");
    setUser(me.data);
  }, []);

  const register = useCallback(
    async (payload: RegisterPayload) => {
      await apiClient.post<User>("/auth/register", payload);
      await login(payload.email, payload.password);
    },
    [login],
  );

  const logout = useCallback(async () => {
    const refreshToken = localStorage.getItem("hm_refresh_token");
    try {
      if (refreshToken) {
        await apiClient.post("/auth/logout", { refresh_token: refreshToken });
      }
    } finally {
      clearTokens();
      setUser(null);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
    }),
    [user, loading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
