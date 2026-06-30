import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    // Point Turbopack at the frontend workspace to suppress the multiple
    // lockfiles warning caused by the root-level package-lock.json.
    root: __dirname,
  },
};

export default nextConfig;
