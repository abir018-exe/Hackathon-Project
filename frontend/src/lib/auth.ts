"use client";

export function getAccessToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("access_token");
  }
  return null;
}

export function getRefreshToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("refresh_token");
  }
  return null;
}

export function setTokens(accessToken: string, refreshToken: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
  }
}

export function clearTokens(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  }
}

export function getUser(): User | null {
  if (typeof window !== "undefined") {
    const userStr = localStorage.getItem("user");
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
  }
  return null;
}

export function setUser(user: User): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("user", JSON.stringify(user));
  }
}

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: "owner" | "admin" | "developer" | "viewer";
}