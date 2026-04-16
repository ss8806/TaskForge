"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { ConfigProvider } from "antd";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  useEffect(() => {
    // 管理者権限チェック
    const checkAdminAccess = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) {
        router.push("/login");
        return;
      }

      try {
        const response = await fetch("http://localhost:8000/api/admin/users", {
          headers: { Authorization: `Bearer ${token}` },
        });
        
        if (response.status === 403) {
          router.push("/dashboard");
        }
      } catch (error) {
        console.error("Admin access check failed:", error);
        router.push("/login");
      }
    };

    checkAdminAccess();
  },[router]);

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: "#2563eb",
        },
      }}
    >
      {children}
    </ConfigProvider>
  );
}