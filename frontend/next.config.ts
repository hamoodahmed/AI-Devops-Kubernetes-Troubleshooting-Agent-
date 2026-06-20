/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // <-- this creates an 'out' folder
  typescript: { ignoreBuildErrors: true },
  eslint: { ignoreDuringBuilds: true },
}
module.exports = nextConfig