import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ['10.17.7.218', 'localhost'],
  devIndicators: false,
  env: {
    VITE_API_URL: process.env.VITE_API_URL,
  },
};

export default nextConfig;
