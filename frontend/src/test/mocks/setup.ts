import { worker } from "./handlers";

// テスト環境でMSWを開始
export async function setupMocks() {
  if (typeof window !== "undefined") {
    worker.start({
      onUnhandledRequest: "bypass", // モックされていないリクエストはそのまま通過
    });
  }
}
