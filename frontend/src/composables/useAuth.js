import { reactive } from "vue";

const state = reactive({
	user: null,
	fullName: null,
	roles: [],
	isLoggedIn: false,
	ready: false,
});

const headers = {
	Accept: "application/json",
	"Content-Type": "application/json",
	"X-Frappe-CSRF-Token": "fetch",
	"X-Requested-With": "XMLHttpRequest",
};

export function useAuthStore() {
	async function login(usr, pwd) {
		const res = await fetch("/api/method/login", {
			method: "POST",
			credentials: "include",
			headers,
			body: JSON.stringify({ usr, pwd }),
		});
		const data = await res.json();
		if (data.message === "Logged In") {
			await fetchUser();
			state.ready = true;
			return true;
		}
		return false;
	}

	async function fetchUser() {
		try {
			const res = await fetch("/api/method/frappe.auth.get_logged_user", {
				credentials: "include",
				headers,
			});
			const data = await res.json();
			state.user = data.message;
			state.isLoggedIn = !!data.message && data.message !== "Guest";
			if (state.isLoggedIn) {
				await fetchRoles();
			} else {
				state.fullName = null;
				state.roles = [];
			}
		} catch (e) {
			console.error("fetchUser error", e);
			state.user = null;
			state.fullName = null;
			state.roles = [];
			state.isLoggedIn = false;
		} finally {
			state.ready = true; // ✅ always mark ready
		}
	}

	async function fetchRoles() {
		try {
			const res = await fetch("/api/method/intern_test.api.get_current_user_info", {
				method: "GET",
				credentials: "include",
				headers,
			});
			const data = await res.json();
			const info = data.message || {};
			state.fullName = info.full_name || "";
			state.roles = info.roles || [];
		} catch (e) {
			console.error("fetchRoles error", e);
		}
	}

	async function logout() {
		await fetch("/api/method/logout", { credentials: "include", headers });
		state.user = null;
		state.fullName = null;
		state.roles = [];
		state.isLoggedIn = false;
		state.ready = true;
	}

	function hasRole(role) {
		return state.roles.includes(role);
	}

	function requireRoles(rolesArr) {
		if (hasRole("TSF Admin")) return true;
		return rolesArr.some((r) => hasRole(r));
	}

	// ✅ Return state directly with getters — NOT ...state spread
	return {
		get user() {
			return state.user;
		},
		get fullName() {
			return state.fullName;
		},
		get roles() {
			return state.roles;
		},
		get isLoggedIn() {
			return state.isLoggedIn;
		},
		get ready() {
			return state.ready;
		},
		set ready(v) {
			state.ready = v;
		},
		login,
		logout,
		fetchUser,
		fetchRoles,
		hasRole,
		requireRoles,
	};
}
