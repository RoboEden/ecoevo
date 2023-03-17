import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react'


export default defineConfig({
    build:
    {
        outDir: '../ecoevo/webapp/static/',
        emptyOutDir: true,
        sourcemap: true
    },
    plugins: [
        react({ include: './client/', })
    ],
});