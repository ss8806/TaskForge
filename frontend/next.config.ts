import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Turbopackのワークスペースルート設定
  turbopack: {
    root: ".",
  },
  // 明示的にルートディレクトリを設定
  distDir: ".next",
};

export default nextConfig;
