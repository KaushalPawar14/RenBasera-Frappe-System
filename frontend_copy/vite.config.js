// import { defineConfig } from "vite";
// import vue from "@vitejs/plugin-vue";
// import { VitePWA } from "vite-plugin-pwa";
// import http from "http"; // ✅ add this import

// export default defineConfig({
// 	plugins: [
// 		vue(),
// 		VitePWA({
// 			/* ...your existing PWA config... */
// 		}),
// 	],
// 	server: {
// 		host: "0.0.0.0",
// 		port: 5173,
// 		proxy: {
// 			"/api": {
// 				target: "http://192.168.3.144:8000",
// 				changeOrigin: true,
// 				secure: false,
// 				// ✅ Custom agent that disables Expect: 100-continue at the Node level
// 				agent: new http.Agent({ keepAlive: true }),
// 				configure: (proxy) => {
// 					proxy.on("proxyReq", (proxyReq, req) => {
// 						// Remove Expect header at proxy level
// 						proxyReq.removeHeader("Expect");
// 						proxyReq.removeHeader("expect");
// 						proxyReq.setHeader("X-Requested-With", "XMLHttpRequest");
// 						proxyReq.setHeader("X-Frappe-CSRF-Token", "fetch");
// 					});
// 					proxy.on("proxyRes", (proxyRes) => {
// 						const cookies = proxyRes.headers["set-cookie"];
// 						if (cookies) {
// 							proxyRes.headers["set-cookie"] = cookies.map((cookie) =>
// 								cookie
// 									.replace(/;\s*Domain=[^;]*/gi, "")
// 									.replace(/;\s*SameSite=Strict/gi, "; SameSite=Lax")
// 									.replace(/;\s*Secure/gi, ""),
// 							);
// 						}
// 					});
// 					proxy.on("error", (err, req, res) => {
// 						console.error("Proxy error:", err.message);
// 						try {
// 							res.writeHead(500, { "Content-Type": "application/json" });
// 							res.end(JSON.stringify({ error: true, message: err.message }));
// 						} catch (e) {}
// 					});
// 				},
// 			},
// 		},
// 	},
// });

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
	plugins: [vue()],
	server: {
		host: true,
		proxy: {
			// Whenever Vue sees a request starting with /api,
			// it silently forwards it to your Frappe backend.
			"/api": {
				target: "http://192.168.3.144:8000",
				changeOrigin: true,
			},
		},
	},
});
