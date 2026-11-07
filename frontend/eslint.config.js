import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default tseslint.config(
  {
    ignores: ['dist/**', 'node_modules/**', 'coverage/**', 'playwright-report/**', 'test-results/**'],
  },
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: 'module',
      parserOptions: { project: ['./tsconfig.app.json', './tsconfig.node.json'] },
      globals: {
        window: true, document: true, navigator: true, location: true, console: true,
        setTimeout: true, clearTimeout: true, setInterval: true, clearInterval: true,
        fetch: true, Request: true, Response: true, File: true, FormData: true,
        Blob: true, URL: true, localStorage: true, sessionStorage: true, crypto: true,
        React: true, JSX: true,
      },
    },
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': 'off',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-console': 'off',
    },
  },
)
