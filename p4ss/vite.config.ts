import path from 'path'
import { defineConfig, loadEnv } from 'vite'
import autoprefixer from 'autoprefixer'
import tailwindcss from 'tailwindcss'
import vue from '@vitejs/plugin-vue'
import svgLoader from 'vite-svg-loader'
import { compression } from 'vite-plugin-compression2'

process.env.VITE_BUILDTIME = `${new Date()}`

export default defineConfig(env => ({
  base: loadEnv(env.mode, process.cwd()).VITE_PUBLIC_PATH,
  server: {
    host: 'localhost',
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://47.96.82.12:8080/api',
        changeOrigin: true,
        ws: true,
        rewrite: path => path.replace(/^\/api/, '')
      }
    }
  },
  preview: {
    host: 'localhost',
    port: 5173
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        charset: false
      }
    },
    postcss: {
      plugins: [autoprefixer(), tailwindcss()]
    }
  },
  plugins: [vue(), svgLoader(), compression()],
  build: {
    sourcemap: false,
    assetsInlineLimit: 4 * 1024
  }
}))
