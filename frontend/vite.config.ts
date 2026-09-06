import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The app is developed OUTSIDE the bench (symlinked in), so Doppio's default
// `require('../../../sites/common_site_config.json')` in proxyOptions.ts resolves
// against the real repo path and fails the build. We inline a dev-only proxy to
// the bench web port instead (override with FRAPPE_BACKEND). The proxy is only
// used by `vite dev`; production serves the built assets through Frappe, so the
// build never needs it.
const BACKEND = process.env.FRAPPE_BACKEND || 'http://knc.localhost:8001';

export default defineConfig(({ command }) => ({
	plugins: [react()],
	server: {
		port: 8080,
		host: '0.0.0.0',
		proxy:
			command === 'serve'
				? {
						'^/(app|api|assets|files|private)': {
							target: BACKEND,
							ws: true,
							changeOrigin: true,
						},
					}
				: undefined,
	},
	resolve: {
		alias: {
			'@': path.resolve(__dirname, 'src'),
		},
	},
	build: {
		outDir: '../knc/public/frontend',
		emptyOutDir: true,
		target: 'es2015',
	},
}));
