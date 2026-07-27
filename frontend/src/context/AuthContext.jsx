import { createContext, useContext, useState, useCallback } from "react";
import { loginUser, registerUser } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });

  const login = useCallback(async ({ email, password }) => {
    const data = await loginUser({ email, password });
    localStorage.setItem("token", data.token);
    setToken(data.token);
    // Backend login response doesn't include user profile details beyond
    // the token, so store what we know locally (email); profile can be
    // fetched separately via /api/auth/profile if needed.
    const minimalUser = { email };
    localStorage.setItem("user", JSON.stringify(minimalUser));
    setUser(minimalUser);
    return data;
  }, []);

  const register = useCallback(async ({ username, email, password }) => {
    return registerUser({ username, email, password });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
  }, []);

  const value = {
    token,
    user,
    isAuthenticated: !!token,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
