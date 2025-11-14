/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/:path*',
      },
    ];
  },
  // Ensure path aliases work correctly in Railway build
  webpack: (config, { isServer }) => {
    // Resolve @ alias to current directory (frontend/)
    const aliasPath = path.resolve(__dirname);
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': aliasPath,
    };
    
    // Also ensure modules resolve correctly
    config.resolve.modules = [
      path.resolve(__dirname, 'node_modules'),
      'node_modules',
    ];
    
    return config;
  },
};

module.exports = nextConfig;

