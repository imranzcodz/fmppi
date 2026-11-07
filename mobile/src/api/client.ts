import axios, { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig } from "axios";
import * as SecureStore from "expo-secure-store";
import { API_BASE_URL, ENDPOINTS } from "./endpoints";
import { LoginResponse, TokenPayload } from "./types";

const TOKEN_KEY = "fmppi_auth_tokens";

export interface StoredTokens {
  access_token: string;
  refresh_token: string;
}

// ---------------------------------------------------------------------------
// Secure token storage (async)
// ---------------------------------------------------------------------------

export const secureStorage = {
  async getTokens(): Promise<StoredTokens | null> {
    try {
      const raw = await SecureStore.getItemAsync(TOKEN_KEY);
      if (!raw) return null;
      return JSON.parse(raw) as StoredTokens;
    } catch {
      return null;
    }
  },

  async setTokens(tokens: StoredTokens): Promise<void> {
    await SecureStore.setItemAsync(TOKEN_KEY, JSON.stringify(tokens));
  },

  async clearTokens(): Promise<void> {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
  },
};

// ---------------------------------------------------------------------------
// Axios client with JWT access-token interceptor + 401 refresh handling.
//
// Tokens are cached in memory after load so the (synchronous) request
// interceptor can attach the access token without awaiting secure-store.
// ---------------------------------------------------------------------------

export class ApiClient {
  private client: AxiosInstance;
  private cachedTokens: StoredTokens | null = null;
  private refreshing = false;
  private refreshSubscribers: ((token: string) => void)[] = [];

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    });

    this.client.interceptors.request.use(
      this.attachAccessToken,
      this.onRequestError
    );

    this.client.interceptors.response.use(
      (resp) => resp,
      this.onResponseError.bind(this)
    );
  }

  /** Load tokens from secure store into the in-memory cache. Call on app start. */
  async loadTokens(): Promise<void> {
    this.cachedTokens = await secureStorage.getTokens();
  }

  /** Replace the cached tokens (used after login / logout). */
  setCachedTokens(tokens: StoredTokens | null): void {
    this.cachedTokens = tokens;
  }

  private attachAccessToken = (
    config: InternalAxiosRequestConfig
  ): InternalAxiosRequestConfig => {
    if (this.cachedTokens?.access_token) {
      config.headers.Authorization = `Bearer ${this.cachedTokens.access_token}`;
    }
    return config;
  };

  private onRequestError = (error: unknown): Promise<never> =>
    Promise.reject(error);

  private async onResponseError(error: unknown): Promise<never> {
    const original = (error as any)?.config;
    const status = (error as any)?.response?.status;

    if (status === 401 && original && !original._retry) {
      original._retry = true;

      if (!this.refreshing) {
        this.refreshing = true;
        try {
          const refreshed = await this.refreshAccessToken(
            this.cachedTokens?.refresh_token ?? ""
          );
          await secureStorage.setTokens(refreshed);
          this.cachedTokens = refreshed;
          this.refreshSubscribers.forEach((cb) => cb(refreshed.access_token));
          this.refreshSubscribers = [];
          return this.client(original);
        } catch (refreshErr) {
          this.refreshSubscribers = [];
          this.cachedTokens = null;
          await secureStorage.clearTokens();
          return Promise.reject(refreshErr);
        } finally {
          this.refreshing = false;
        }
      }

      return new Promise((resolve, reject) => {
        this.refreshSubscribers.push((accessToken: string) => {
          original.headers.Authorization = `Bearer ${accessToken}`;
          resolve(this.client(original));
        });
      });
    }

    return Promise.reject(error);
  }

  async refreshAccessToken(refreshToken: string): Promise<StoredTokens> {
    const { data } = await this.client.post<TokenPayload>(
      ENDPOINTS.auth.refresh,
      { refresh_token: refreshToken }
    );
    return {
      access_token: data.access_token,
      refresh_token: data.refresh_token ?? refreshToken,
    };
  }

  get<T = unknown>(url: string, config?: AxiosRequestConfig) {
    return this.client.get<T>(url, config);
  }

  post<T = unknown>(url: string, body?: unknown, config?: AxiosRequestConfig) {
    return this.client.post<T>(url, body, config);
  }

  put<T = unknown>(url: string, body?: unknown, config?: AxiosRequestConfig) {
    return this.client.put<T>(url, body, config);
  }

  delete<T = unknown>(url: string, config?: AxiosRequestConfig) {
    return this.client.delete<T>(url, config);
  }

  postForm<T = unknown>(
    url: string,
    formData: FormData,
    config?: AxiosRequestConfig
  ) {
    return this.client.post<T>(url, formData, {
      ...config,
      headers: {
        ...config?.headers,
        "Content-Type": "multipart/form-data",
      },
    });
  }
}

export const api = new ApiClient();

// Auth helpers used by auth service / screens
export const authService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const { data } = await api.post<LoginResponse>(ENDPOINTS.auth.login, {
      email,
      password,
    });
    await secureStorage.setTokens({
      access_token: data.access_token,
      refresh_token: data.refresh_token,
    });
    api.setCachedTokens({
      access_token: data.access_token,
      refresh_token: data.refresh_token,
    });
    return data;
  },

  async register(payload: {
    email: string;
    password: string;
    full_name?: string;
    role?: string;
  }) {
    return api.post(ENDPOINTS.auth.register, payload);
  },

  async mfaVerify(userId: string, code: string) {
    return api.post(ENDPOINTS.auth.mfaVerify, { user_id: userId, code });
  },

  async logout() {
    await secureStorage.clearTokens();
    api.setCachedTokens(null);
  },

  async isAuthenticated(): Promise<boolean> {
    const tokens = await secureStorage.getTokens();
    return !!tokens?.access_token;
  },
};
