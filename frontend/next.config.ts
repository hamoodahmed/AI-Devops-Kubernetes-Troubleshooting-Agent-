/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,   // <-- this is key
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  output: 'standalone',
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
  },
}

module.exports = nextConfig
