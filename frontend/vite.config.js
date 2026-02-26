import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
	plugins: [
		vue(),
		VitePWA({
			registerType: "autoUpdate",
			includeAssets: ["favicon.ico", "icon-192.png", "icon-512.png"],
			manifest: {
				name: "TSF Distribution",
				short_name: "TSF Dist",
				description: "TSF Tiffin Distribution Management",
				theme_color: "#2e7d32",
				background_color: "#ffffff",
				display: "standalone",
				orientation: "portrait",
				scope: "/",
				start_url: "/",
				icons: [
					{ src: "icon-192.png", sizes: "192x192", type: "image/png" },
					{ src: "icon-512.png", sizes: "512x512", type: "image/png" },
				],
			},
			workbox: {
				globPatterns: ["**/*.{js,css,html,ico,png,svg}"],
			},
		}),
	],
	server: {
		host: "0.0.0.0",
		port: 5173,
		proxy: {
			"/api": {
				target: "http://192.168.3.144:8000",
				changeOrigin: true,
				secure: false,
				// ❌ REMOVED cookieDomainRewrite — it was breaking the Frappe session cookie,
				//    causing Frappe to treat every request as a new/anonymous session with no CSRF token
				configure: (proxy) => {
					proxy.on("proxyReq", (proxyReq, req, res) => {
						// Remove Expect header — prevents 417 errors
						proxyReq.removeHeader("Expect");
						proxyReq.removeHeader("expect");
						proxyReq.setHeader("X-Requested-With", "XMLHttpRequest");
						// 'fetch' tells Frappe to validate CSRF via the session cookie directly.
						// This works because the proxy makes Frappe see the request as same-origin.
						proxyReq.setHeader("X-Frappe-CSRF-Token", "fetch");
					});
					proxy.on("proxyRes", (proxyRes, req, res) => {
						// Strip the domain/path restrictions from Set-Cookie headers so the
						// browser correctly stores Frappe's session cookies for localhost
						const cookies = proxyRes.headers["set-cookie"];
						if (cookies) {
							proxyRes.headers["set-cookie"] = cookies.map((cookie) =>
								cookie
									.replace(/;\s*Domain=[^;]*/gi, "")
									.replace(/;\s*SameSite=Strict/gi, "; SameSite=Lax")
									.replace(/;\s*Secure/gi, ""),
							);
						}
					});
					proxy.on("error", (err, req, res) => {
						console.error("Proxy error:", err.message);
						try {
							res.writeHead(500, { "Content-Type": "application/json" });
							res.end(JSON.stringify({ error: true, message: err.message }));
						} catch (e) {}
					});
				},
			},
		},
	},
});
