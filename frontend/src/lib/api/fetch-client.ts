import { useAuthStore } from '@/hooks/use-auth-store';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiFetchOptions extends RequestInit {
    params?: Record<string, any>;
}

export async function apiFetch<T>(endpoint: string, options: ApiFetchOptions = {}): Promise<T> {
    const { params, ...init } = options;
    const token = useAuthStore.getState().token;

    // URLとクエリパラメータの構築
    const url = new URL(endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`);
    if (params) {
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                url.searchParams.append(key, String(value));
            }
        });
    }

    // デフォルトヘッダーの設定
    const headers = new Headers(init.headers);
    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }
    if (!(init.body instanceof FormData) && !headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(url.toString(), {
        ...init,
        headers,
    });

    // 401エラー（認証切れ）のハンドリング
    if (response.status === 401 && typeof window !== 'undefined') {
        useAuthStore.getState().logout();
        if (window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
        throw new Error('Unauthorized');
    }

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API error: ${response.status}`);
    }

    // 204 No Content の場合は null を返す
    if (response.status === 204) {
        return null as T;
    }

    return response.json();
}
