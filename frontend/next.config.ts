import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  basePath: '/learning', // 👈 ¡Esto es la clave!
  images: {
    unoptimized: true, // Necesario para 'export' si usas <Image />
  },
};

export default nextConfig;
