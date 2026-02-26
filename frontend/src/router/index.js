import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../composables/useAuth";

const routes = [
	{ path: "/", redirect: "/login" },

	{ path: "/login", component: () => import("../pages/Login.vue"), meta: { public: true } },
	{
		path: "/unauthorized",
		component: () => import("../pages/Unauthorized.vue"),
		meta: { public: true },
	},

	// Dashboard (all logged-in roles)
	{
		path: "/dashboard",
		component: () => import("../pages/Dashboard.vue"),
		meta: { requiresAuth: true },
	},

	// Challan - Distribution Manager / Admin
	{
		path: "/challan",
		component: () => import("../pages/DispatchChallan.vue"),
		meta: { requiresAuth: true, roles: ["TSF Distribution Manager", "TSF Admin"] },
	},

	// Challan Detail - Distribution Manager / Admin / Supervisor / Security Guard (optional)
	{
		path: "/challan/:name",
		component: () => import("../pages/ChallanDetail.vue"),
		meta: {
			requiresAuth: true,
			roles: [
				"TSF Distribution Manager",
				"TSF Admin",
				"TSF Supervisor",
				"TSF Security Guard",
			],
		},
	},

	// Security Check - Security Guard / Admin
	{
		path: "/security-check",
		component: () => import("../pages/SecurityCheck.vue"),
		meta: { requiresAuth: true, roles: ["TSF Security Guard", "TSF Admin"] },
	},

	// Delivery Log - Driver / Admin / Supervisor
	{
		path: "/delivery-log",
		component: () => import("../pages/DeliveryLog.vue"),
		meta: { requiresAuth: true, roles: ["TSF Driver", "TSF Admin", "TSF Supervisor"] },
	},

	// Return Trip - Driver / Admin / Supervisor
	{
		path: "/return-trip",
		component: () => import("../pages/ReturnTrip.vue"),
		meta: { requiresAuth: true, roles: ["TSF Driver", "TSF Admin", "TSF Supervisor"] },
	},
];

const router = createRouter({
	history: createWebHistory(),
	routes,
});

router.beforeEach(async (to) => {
	const auth = useAuthStore();

	if (to.meta.public) return true;

	if (!auth.ready) {
		await auth.fetchUser();
		auth.ready = true;
	}

	if (!auth.isLoggedIn) return "/login";

	if (to.meta.roles && Array.isArray(to.meta.roles)) {
		const ok = auth.requireRoles(to.meta.roles);
		if (!ok) return "/unauthorized";
	}

	return true;
});

export default router;
