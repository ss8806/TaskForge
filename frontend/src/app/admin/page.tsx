"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, Typography, Button, Space, Table, message } from "antd";
import type { TableColumnsType } from "antd";

const { Title, Text } = Typography;

interface User {
  id: number;
  email: string;
  role: string;
  created_at: string;
}

interface Project {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  created_at: string;
}

export default function AdminPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) {
        router.push("/login");
        return;
      }

      try {
        // ユーザーデータ取得
        const usersResponse = await fetch("http://localhost:8000/api/admin/users", {
          headers: { Authorization: `Bearer ${token}` },
        });
        
        if (usersResponse.status === 403) {
          message.error("管理者権限がありません");
          router.push("/dashboard");
          return;
        }
        
        if (usersResponse.ok) {
          const usersData = await usersResponse.json();
          setUsers(usersData);
        }

        // プロジェクトデータ取得
        const projectsResponse = await fetch("http://localhost:8000/api/admin/projects", {
          headers: { Authorization: `Bearer ${token}` },
        });
        
        if (projectsResponse.ok) {
          const projectsData = await projectsResponse.json();
          setProjects(projectsData);
        }
      } catch (error) {
        message.error("データの取得に失敗しました");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router]);

  const userColumns: TableColumnsType<User> = [
    {
      title: "ID",
      dataIndex: "id",
      key: "id",
    },
    {
      title: "メールアドレス",
      dataIndex: "email",
      key: "email",
    },
    {
      title: "権限",
      dataIndex: "role",
      key: "role",
      render: (role: string) => (
        <span style={{ color: role === "admin" ? "#1890ff" : "#52c41a" }}>
          {role === "admin" ? "管理者" : "一般ユーザー"}
        </span>
      ),
    },
    {
      title: "登録日時",
      dataIndex: "created_at",
      key: "created_at",
      render: (date: string) => new Date(date).toLocaleString("ja-JP"),
    },
    {
      title: "操作",
      key: "actions",
      render: (_, record) => (
        <Space>
          {record.role === "user" && (
            <Button
              size="small"
              type="primary"
              onClick={() => handleMakeAdmin(record.id)}
            >
              管理者に昇格
            </Button>
          )}
          {record.role === "admin" && record.id !== 1 && (
            <Button
              size="small"
              danger
              onClick={() => handleRevokeAdmin(record.id)}
            >
              管理者権限剥奪
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const projectColumns: TableColumnsType<Project> = [
    {
      title: "ID",
      dataIndex: "id",
      key: "id",
    },
    {
      title: "プロジェクト名",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "説明",
      dataIndex: "description",
      key: "description",
      render: (desc: string | null) => desc || "-",
    },
    {
      title: "オーナーID",
      dataIndex: "owner_id",
      key: "owner_id",
    },
    {
      title: "作成日時",
      dataIndex: "created_at",
      key: "created_at",
      render: (date: string) => new Date(date).toLocaleString("ja-JP"),
    },
  ];

  const handleMakeAdmin = async (userId: number) => {
    const token = localStorage.getItem("access_token");
    try {
      const response = await fetch(`http://localhost:8000/api/admin/users/${userId}/make-admin`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      
      if (response.ok) {
        message.success("ユーザーを管理者に昇格しました");
        // データ再取得
        const usersResponse = await fetch("http://localhost:8000/api/admin/users", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (usersResponse.ok) {
          const usersData = await usersResponse.json();
          setUsers(usersData);
        }
      } else {
        message.error("操作に失敗しました");
      }
    } catch (error) {
      message.error("エラーが発生しました");
    }
  };

  const handleRevokeAdmin = async (userId: number) => {
    const token = localStorage.getItem("access_token");
    try {
      const response = await fetch(`http://localhost:8000/api/admin/users/${userId}/revoke-admin`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      
      if (response.ok) {
        message.success("管理者権限を剥奪しました");
        // データ再取得
        const usersResponse = await fetch("http://localhost:8000/api/admin/users", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (usersResponse.ok) {
          const usersData = await usersResponse.json();
          setUsers(usersData);
        }
      } else {
        message.error("操作に失敗しました");
      }
    } catch (error) {
      message.error("エラーが発生しました");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    router.push("/login");
  };

  if (loading) {
    return <div style={{ padding: "24px", textAlign: "center" }}>読み込み中...</div>;
  }

  return (
    <div style={{ padding: "24px", maxWidth: "1200px", margin: "0 auto" }}>
      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <Card>
          <Space direction="vertical" style={{ width: "100%" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <Title level={2}>管理者ダッシュボード</Title>
              <Button danger onClick={handleLogout}>
                ログアウト
              </Button>
            </div>
            <Text>システム全体の管理と監視を行います。</Text>
          </Space>
        </Card>

        <Card title="ユーザー管理">
          <Table
            columns={userColumns}
            dataSource={users}
            rowKey="id"
            pagination={{ pageSize: 10 }}
            loading={loading}
          />
        </Card>

        <Card title="プロジェクト管理">
          <Table
            columns={projectColumns}
            dataSource={projects}
            rowKey="id"
            pagination={{ pageSize: 10 }}
            loading={loading}
          />
        </Card>

        <Card title="システム情報">
          <Space direction="vertical">
            <Text>総ユーザー数: {users.length}人</Text>
            <Text>総プロジェクト数: {projects.length}件</Text>
            <Text>管理者数: {users.filter(u => u.role === "admin").length}人</Text>
          </Space>
        </Card>
      </Space>
    </div>
  );
}