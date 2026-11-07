import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  // @ts-expect-error - test property added by vitest plugin
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    globals: true,
    exclude: ['node_modules/**', 'e2e/**', 'dist/**', 'coverage/**', 'dist-ssr/**', 'local**'],
  },
})
