import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    // Point Turbopack at the frontend workspace to suppress the multiple
    // lockfiles warning caused by the root-level package-lock.json.
    root: __dirname,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination:
          process.env.NODE_ENV === "development"
            ? "http://127.0.0.1:8000/api/:path*"
            : "/api/",
      },
    ];
  },
};

export default nextConfig;
