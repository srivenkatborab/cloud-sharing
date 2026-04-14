/**
 * Client-side auth helpers.
 *
 * Tokens are stored in localStorage after login.
 * Server-side rendering does not rely on these functions.
 */

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export function getUserEmail(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("user_email");
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

export function saveTokens(tokens: {
  access_token: string;
  id_token: string;
  refresh_token: string;
  email?: string;
}) {
  localStorage.setItem("access_token", tokens.access_token);
  localStorage.setItem("id_token", tokens.id_token);
  localStorage.setItem("refresh_token", tokens.refresh_token);
  if (tokens.email) {
    localStorage.setItem("user_email", tokens.email);
  }
}

export function logout() {
  localStorage.clear();
  window.location.href = "/";
}
