import requests
import json

BASE_URL = "http://localhost:8000/api"

def get_auth_token(email="test@example.com", password="testpassword123"):
    """認証トークンを取得"""
    url = f"{BASE_URL}/auth/login"
    data = {"email": email, "password": password}
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def test_admin_access():
    """管理者権限テスト"""
    print("\n=== 管理者権限テスト ===")
    
    # 一般ユーザートークン取得（管理者権限なし）
    user_token = get_auth_token()
    if not user_token:
        print("一般ユーザートークン取得失敗")
        return
    
    # 管理者APIにアクセス（403エラーになるはず）
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    
    print(f"一般ユーザーの管理者APIアクセス:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Expected: 403 (Forbidden)")
    
    if response.status_code == 403:
        print("  ✅ 一般ユーザーは管理者APIにアクセス不可")
    else:
        print(f"  ❌ 予期しないレスポンス: {response.text}")

def test_user_registration():
    """ユーザー登録テスト"""
    print("\n=== ユーザー登録テスト ===")
    
    # 新しいユーザー登録
    url = f"{BASE_URL}/auth/register"
    data = {
        "email": f"test_admin_{hash('test')}@example.com",
        "password": "adminpassword123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ ユーザー登録成功")
            token = response.json()["access_token"]
            return token
        else:
            print(f"❌ ユーザー登録失敗: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_admin_user_management():
    """管理者ユーザー管理テスト（管理者権限が必要）"""
    print("\n=== 管理者ユーザー管理テスト ===")
    
    # 管理者トークンが必要（実際の管理者ユーザーでテスト）
    admin_token = get_auth_token("admin@example.com", "adminpassword")
    if not admin_token:
        print("管理者トークン取得失敗 - スキップ")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # ユーザー一覧取得
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    print(f"管理者ユーザー一覧取得:")
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        users = response.json()
        print(f"  ✅ ユーザー数: {len(users)}")
        
        # 最初のユーザーを管理者に昇格
        if users:
            user_id = users[0]["id"]
            promote_url = f"{BASE_URL}/admin/users/{user_id}/make-admin"
            promote_response = requests.post(promote_url, headers=headers)
            
            print(f"\nユーザー管理者昇格:")
            print(f"  Status Code: {promote_response.status_code}")
            print(f"  Response: {promote_response.text}")
    else:
        print(f"  ❌ ユーザー一覧取得失敗: {response.text}")

def test_ai_workflow():
    """AIワークフローテスト"""
    print("\n=== AIワークフローテスト ===")
    
    token = get_auth_token()
    if not token:
        print("トークン取得失敗 - スキップ")
        return
    
    # プロジェクト作成（テスト用）
    headers = {"Authorization": f"Bearer {token}"}
    project_data = {"name": "AI Test Project", "description": "AIワークフローテスト用"}
    project_response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers)
    
    if project_response.status_code != 201:
        print("プロジェクト作成失敗 - スキップ")
        return
    
    project_id = project_response.json()["id"]
    
    # AIタスク分解実行
    ai_url = f"{BASE_URL}/projects/{project_id}/ai/decompose"
    ai_data = {"prompt": "シンプルなTODOアプリを作りたい", "sprint_id": None}
    
    try:
        response = requests.post(ai_url, json=ai_data, headers=headers)
        print(f"AIタスク分解実行:")
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ エピック数: {len(result.get('epics', []))}")
            print(f"  ✅ タスク数: {len(result.get('tasks', []))}")
            print(f"  ✅ スプリント数: {len(result.get('sprints', []))}")
        else:
            print(f"  ❌ AI処理失敗: {response.text}")
    except Exception as e:
        print(f"  ❌ エラー: {e}")

if __name__ == "__main__":
    print("TaskForge Phase 3 テスト実行")
    print("=" * 50)
    
    # テスト実行
    test_user_registration()
    test_admin_access()
    test_admin_user_management()
    test_ai_workflow()
    
    print("\n" + "=" * 50)
    print("テスト完了")