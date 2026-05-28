/** @type {import('next').NextConfig} */
const nextConfig = {
  // Permite imágenes desde el servidor de documentos
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
  },
};

export default nextConfig;
