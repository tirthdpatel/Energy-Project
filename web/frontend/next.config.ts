import type { NextConfig } from "next";

// Base URL of the FastAPI backend.
//   - Local dev: the uvicorn server on port 8000.
//   - Production: the Render service, overridable with the API_BASE_URL env var
//     (note: rewrites are baked in at BUILD time, so set it before building).
// Requests are proxied server-side through Next.js rewrites, so the browser only
// ever talks to same-origin /api/* paths and no CORS preflight is involved.
const RENDER_API_URL = "https://energy-project-api-atfu.onrender.com";

const API_BASE_URL =
    process.env.API_BASE_URL?.replace(/\/+$/, "") ||
    (process.env.NODE_ENV === "development"
        ? "http://127.0.0.1:8000"
        : RENDER_API_URL);

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
