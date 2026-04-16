import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
    token: string | null;
    setToken: (token: string | null) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            token: null,
            setToken: (token) => {
                if (token) localStorage.setItem('access_token', token);
                else localStorage.removeItem('access_token');
                set({ token });
            },
            logout: () => {
                localStorage.removeItem('access_token');
                set({ token: null });
                window.location.href = '/login';
            },
        }),
        {
            name: 'auth-storage',
        }
    )
);
