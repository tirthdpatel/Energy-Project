import type { NextConfig } from "next";

// Base URL of the FastAPI backend.
//   - Local dev: the uvicorn server on port 8000.
//   - Production: the Render service URL, supplied via the API_BASE_URL env var.
// Requests are proxied server-side through Next.js rewrites, so the browser only
// ever talks to same-origin /api/* paths and no CORS preflight is involved.
const API_BASE_URL =
    process.env.API_BASE_URL?.replace(/\/+$/, "") || "http://127.0.0.1:8000";

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
                destination: `${API_BASE_URL}/api/:path*`,
            },
        ];
    },
};

export default nextConfig;
