/**
 * Axios API client.
 *
 * Automatically attaches the Cognito access_token from localStorage to
 * every request as a Bearer token. Clears localStorage and redirects to
 * /login when a 401 response is received (token expired or invalid).
 */

import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

// Attach Bearer token to every outgoing request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Redirect to login on 401 (expired/invalid token)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.clear();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
