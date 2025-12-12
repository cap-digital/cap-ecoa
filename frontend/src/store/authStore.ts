import { create } from "zustand";
import { persist } from "zustand/middleware";
import { authApi } from "../services/api";

interface User {
  id: string;
  email: string;
  full_name: string | null;
  political_name: string | null;
  party: string | null;
  state: string | null;
  avatar_url: string | null;
  plan_type: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;

  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    political_name?: string;
    party?: string;
    state?: string;
  }) => Promise<void>;
  logout: () => void;
  updateUser: (data: { full_name?: string; political_name?: string; party?: string; state?: string }) => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,

      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login(email, password);
          const { access_token, user } = response.data;

          localStorage.setItem("access_token", access_token);

          set({
            user,
            token: access_token,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.response?.data?.detail || "Erro ao fazer login",
          });
          throw error;
        }
      },

      register: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.register(data);
          const { access_token, user } = response.data;

          localStorage.setItem("access_token", access_token);

          set({
            user,
            token: access_token,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.response?.data?.detail || "Erro ao criar conta",
          });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem("access_token");
        set({ user: null, token: null });
      },

      updateUser: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.updateMe(data);
          set({ user: response.data, isLoading: false });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.response?.data?.detail || "Erro ao atualizar perfil",
          });
          throw error;
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({ user: state.user, token: state.token }),
    }
  )
);
