import axios, {
  AxiosError,
  AxiosInstance,
  InternalAxiosRequestConfig,
} from "axios";
import type { TokenPair } from "../types";

const ACCESS_KEY = "hm_access_token";
const REFRESH_KEY = "hm_refresh_token";

function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY);
}

function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY);
}

export function setTokens(tokens: TokenPair): void {
  localStorage.setItem(ACCESS_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});

let refreshing: Promise<TokenPair> | null = null;

async function doRefresh(refreshToken: string): Promise<TokenPair> {
  const { data } = await axios.post<TokenPair>(
    `${apiClient.defaults.baseURL}/auth/refresh`,
    { refresh_token: refreshToken },
  );
  setTokens(data);
  return data;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean })
      | undefined;

    if (
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      getRefreshToken()
    ) {
      original._retry = true;
      try {
        if (!refreshing) {
          refreshing = doRefresh(getRefreshToken() as string).finally(() => {
            refreshing = null;
          });
        }
        const tokens = await refreshing;
        original.headers.set("Authorization", `Bearer ${tokens.access_token}`);
        return apiClient(original);
      } catch {
        clearTokens();
        if (typeof window !== "undefined") {
          window.location.assign("/login");
        }
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  },
);

export default apiClient;
