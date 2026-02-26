<template>
	<div class="page">
		<!-- Hero Header -->
		<div class="hero">
			<div class="hero-bg"></div>
			<div class="hero-content">
				<div class="hero-top">
					<div class="avatar-wrap">
						<div class="avatar">{{ initials }}</div>
						<div class="avatar-ring"></div>
					</div>
					<button class="logout-btn" @click="handleLogout"><span>↩</span> Logout</button>
				</div>
				<div class="hero-text">
					<div class="greeting">Good {{ timeOfDay }} 👋</div>
					<div class="fullname">{{ auth.fullName || auth.user }}</div>
				</div>
				<div class="role-chips">
					<span class="chip" v-for="role in tsfRoles" :key="role">{{
						role.replace("TSF ", "")
					}}</span>
				</div>
			</div>
		</div>

		<!-- Stats Strip -->
		<div class="stats-strip">
			<div class="stat" v-for="s in statsList" :key="s.label">
				<div class="stat-num" :style="{ color: s.color }">{{ s.value }}</div>
				<div class="stat-label">{{ s.label }}</div>
			</div>
		</div>

		<!-- Quick Actions -->
		<div class="section-wrap">
			<div class="section-header">
				<span class="section-title">Quick Actions</span>
			</div>
			<div class="actions-grid">
				<div
					class="action-card"
					v-for="action in visibleActions"
					:key="action.label"
					@click="router.push(action.path)"
					:style="{ '--accent': action.color }"
				>
					<div class="action-icon-wrap">
						<span class="action-icon">{{ action.icon }}</span>
					</div>
					<div class="action-label">{{ action.label }}</div>
					<div class="action-sub">{{ action.sub }}</div>
					<div class="action-arrow">→</div>
				</div>
			</div>
		</div>

		<!-- Recent Activity -->
		<div class="section-wrap">
			<div class="section-header">
				<span class="section-title">Today's Activity</span>
				<span class="see-all" @click="router.push('/challan')">See all →</span>
			</div>
			<div class="activity-card">
				<div v-if="loadingStats" class="activity-loading">
					<div class="dot-pulse"><span></span><span></span><span></span></div>
				</div>
				<div v-else-if="recentChallans.length === 0" class="activity-empty">
					<span class="activity-empty-icon">📭</span>
					<span>No recent activity</span>
				</div>
				<div v-else>
					<div
						class="activity-row"
						v-for="(c, i) in recentChallans"
						:key="c.name"
						:style="{ animationDelay: i * 0.05 + 's' }"
						@click="router.push('/challan/' + c.name)"
					>
						<div
							class="activity-indicator"
							:class="getStatusClass(c.workflow_state)"
						></div>
						<div class="activity-info">
							<div class="activity-name">{{ c.name }}</div>
							<div class="activity-meta">
								{{ c.vehicle || "No vehicle" }} · {{ formatDate(c.creation) }}
							</div>
						</div>
						<div class="activity-status" :class="getStatusClass(c.workflow_state)">
							{{ c.workflow_state || "Draft" }}
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../composables/useAuth";
import { apiGet, listUrl } from "../utils/api.js";

const router = useRouter();
const auth = useAuthStore();
const loadingStats = ref(true);
const recentChallans = ref([]);
const stats = ref({ total: 0, pending: 0, dispatched: 0, completed: 0 });

const tsfRoles = computed(() => auth.roles.filter((r) => r.startsWith("TSF")));

const initials = computed(() => {
	const name = auth.fullName || auth.user || "U";
	return name
		.split(" ")
		.map((n) => n[0])
		.join("")
		.slice(0, 2)
		.toUpperCase();
});

const timeOfDay = computed(() => {
	const h = new Date().getHours();
	if (h < 12) return "Morning";
	if (h < 17) return "Afternoon";
	return "Evening";
});

const statsList = computed(() => [
	{ label: "Today", value: stats.value.total, color: "#2e7d32" },
	{ label: "Pending", value: stats.value.pending, color: "#e65100" },
	{ label: "Dispatched", value: stats.value.dispatched, color: "#6a1b9a" },
	{ label: "Completed", value: stats.value.completed, color: "#1565c0" },
]);

const allActions = [
	{
		label: "Dispatch Challans",
		sub: "Create & manage trips",
		icon: "📋",
		path: "/challan",
		color: "#2e7d32",
		roles: ["TSF Admin", "TSF Distribution Manager"],
	},
	{
		label: "My Deliveries",
		sub: "Log center deliveries",
		icon: "🚚",
		path: "/delivery-log",
		color: "#1565c0",
		roles: ["TSF Driver"],
	},
	{
		label: "Security Check",
		sub: "Verify vehicles",
		icon: "🔒",
		path: "/security-check",
		color: "#e65100",
		roles: ["TSF Security Guard"],
	},
	{
		label: "Return Trip",
		sub: "Log container returns",
		icon: "🔄",
		path: "/return-trip",
		color: "#6a1b9a",
		roles: ["TSF Driver"],
	},
	{
		label: "Wastage Entry",
		sub: "Record wastage",
		icon: "♻️",
		path: "/wastage",
		color: "#2e7d32",
		roles: ["TSF Admin", "TSF Supervisor"],
	},
	{
		label: "Reports",
		sub: "View analytics",
		icon: "📊",
		path: "/reports",
		color: "#1565c0",
		roles: ["TSF Admin", "TSF Report Viewer"],
	},
];

const visibleActions = computed(() =>
	allActions.filter((a) => a.roles.some((r) => auth.hasRole(r))),
);

function getStatusClass(status) {
	const map = {
		Draft: "st-draft",
		"Pending Security Check": "st-pending",
		"Security Verified": "st-verified",
		Dispatched: "st-dispatched",
		Completed: "st-completed",
		Cancelled: "st-cancelled",
	};
	return map[status] || "st-draft";
}

function formatDate(d) {
	if (!d) return "";
	return new Date(d).toLocaleDateString("en-IN", { day: "2-digit", month: "short" });
}

async function handleLogout() {
	await auth.logout();
	router.push("/login");
}

async function fetchStats() {
	loadingStats.value = true;
	try {
		const today = new Date().toISOString().split("T")[0];
		const res = await apiGet(
			listUrl(
				"TSF Dispatch Challan",
				["name", "vehicle", "workflow_state", "creation"],
				[["creation", "like", today + "%"]],
				50,
				"creation desc",
			),
		);
		const data = res.data || [];
		recentChallans.value = data.slice(0, 6);
		stats.value.total = data.length;
		stats.value.pending = data.filter(
			(c) => c.workflow_state === "Pending Security Check",
		).length;
		stats.value.dispatched = data.filter((c) => c.workflow_state === "Dispatched").length;
		stats.value.completed = data.filter((c) => c.workflow_state === "Completed").length;
	} catch (e) {
		console.error(e);
	}
	loadingStats.value = false;
}

onMounted(() => {
	fetchStats();
});
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@500&display=swap");

* {
	font-family: "DM Sans", sans-serif;
}
.page {
	min-height: 100vh;
	background: #f4f6f4;
	padding-bottom: 2.5rem;
}

/* Hero */
.hero {
	position: relative;
	background: #1a4a1e;
	overflow: hidden;
	padding-bottom: 1.5rem;
}
.hero-bg {
	position: absolute;
	inset: 0;
	background:
		radial-gradient(ellipse at 80% 20%, #2e7d3244 0%, transparent 60%),
		radial-gradient(ellipse at 10% 80%, #81c78433 0%, transparent 50%);
}
.hero-content {
	position: relative;
	padding: 1.1rem 1.1rem 0;
}
.hero-top {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 1rem;
}
.avatar-wrap {
	position: relative;
}
.avatar {
	width: 48px;
	height: 48px;
	background: #2e7d32;
	border: 2.5px solid #81c784;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-weight: 700;
	font-size: 1.1rem;
	color: white;
	font-family: "DM Mono", monospace;
}
.avatar-ring {
	position: absolute;
	inset: -4px;
	border-radius: 50%;
	border: 1.5px solid rgba(129, 199, 132, 0.3);
}
.logout-btn {
	background: rgba(255, 255, 255, 0.08);
	border: 1px solid rgba(255, 255, 255, 0.15);
	color: rgba(255, 255, 255, 0.7);
	padding: 0.45rem 0.9rem;
	border-radius: 20px;
	cursor: pointer;
	font-size: 0.82rem;
	display: flex;
	align-items: center;
	gap: 0.35rem;
}
.greeting {
	font-size: 0.82rem;
	color: rgba(255, 255, 255, 0.55);
	margin-bottom: 0.2rem;
}
.fullname {
	font-size: 1.4rem;
	font-weight: 700;
	color: white;
	letter-spacing: -0.02em;
	margin-bottom: 0.85rem;
}
.role-chips {
	display: flex;
	gap: 0.4rem;
	flex-wrap: wrap;
	padding-bottom: 0.25rem;
}
.chip {
	background: rgba(255, 255, 255, 0.1);
	border: 1px solid rgba(255, 255, 255, 0.15);
	color: rgba(255, 255, 255, 0.8);
	padding: 0.22rem 0.65rem;
	border-radius: 20px;
	font-size: 0.72rem;
	font-weight: 500;
}

/* Stats Strip */
.stats-strip {
	background: white;
	display: flex;
	border-bottom: 1px solid #eee;
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}
.stat {
	flex: 1;
	padding: 0.9rem 0.5rem;
	text-align: center;
	border-right: 1px solid #f0f0f0;
}
.stat:last-child {
	border-right: none;
}
.stat-num {
	font-size: 1.5rem;
	font-weight: 700;
	font-family: "DM Mono", monospace;
	line-height: 1;
}
.stat-label {
	font-size: 0.68rem;
	color: #999;
	margin-top: 0.2rem;
	text-transform: uppercase;
	letter-spacing: 0.04em;
	font-weight: 600;
}

/* Sections */
.section-wrap {
	padding: 1.1rem 1rem 0;
}
.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 0.75rem;
}
.section-title {
	font-size: 0.78rem;
	font-weight: 700;
	color: #888;
	text-transform: uppercase;
	letter-spacing: 0.06em;
}
.see-all {
	font-size: 0.78rem;
	color: #2e7d32;
	font-weight: 600;
	cursor: pointer;
}

/* Actions Grid */
.actions-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 0.65rem;
}
.action-card {
	background: white;
	border-radius: 16px;
	padding: 1rem;
	cursor: pointer;
	position: relative;
	overflow: hidden;
	box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
	transition:
		transform 0.15s,
		box-shadow 0.15s;
	border: 1.5px solid transparent;
}
.action-card::before {
	content: "";
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 3px;
	background: var(--accent);
	opacity: 0.7;
	border-radius: 16px 16px 0 0;
}
.action-card:active {
	transform: scale(0.97);
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}
.action-icon-wrap {
	width: 40px;
	height: 40px;
	background: color-mix(in srgb, var(--accent) 12%, white);
	border-radius: 12px;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 0.6rem;
}
.action-icon {
	font-size: 1.3rem;
}
.action-label {
	font-size: 0.88rem;
	font-weight: 700;
	color: #1a1a1a;
	margin-bottom: 0.2rem;
	line-height: 1.2;
}
.action-sub {
	font-size: 0.72rem;
	color: #aaa;
}
.action-arrow {
	position: absolute;
	bottom: 0.85rem;
	right: 0.85rem;
	font-size: 0.85rem;
	color: var(--accent);
	opacity: 0.6;
}

/* Activity Card */
.activity-card {
	background: white;
	border-radius: 16px;
	overflow: hidden;
	box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.activity-loading {
	display: flex;
	justify-content: center;
	padding: 2rem;
}
.dot-pulse {
	display: flex;
	gap: 0.4rem;
	align-items: center;
}
.dot-pulse span {
	width: 8px;
	height: 8px;
	background: #2e7d32;
	border-radius: 50%;
	animation: pulse 1.2s ease-in-out infinite;
}
.dot-pulse span:nth-child(2) {
	animation-delay: 0.2s;
}
.dot-pulse span:nth-child(3) {
	animation-delay: 0.4s;
}
@keyframes pulse {
	0%,
	100% {
		opacity: 0.3;
		transform: scale(0.8);
	}
	50% {
		opacity: 1;
		transform: scale(1);
	}
}
.activity-empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 0.5rem;
	padding: 2rem;
	color: #ccc;
	font-size: 0.85rem;
}
.activity-empty-icon {
	font-size: 2rem;
}
.activity-row {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	padding: 0.8rem 1rem;
	border-bottom: 1px solid #f8f8f8;
	cursor: pointer;
	animation: fadeIn 0.3s ease both;
}
.activity-row:last-child {
	border-bottom: none;
}
.activity-row:active {
	background: #f9f9f9;
}
@keyframes fadeIn {
	from {
		opacity: 0;
		transform: translateY(6px);
	}
	to {
		opacity: 1;
		transform: none;
	}
}
.activity-indicator {
	width: 8px;
	height: 8px;
	border-radius: 50%;
	flex-shrink: 0;
}
.activity-info {
	flex: 1;
	min-width: 0;
}
.activity-name {
	font-size: 0.88rem;
	font-weight: 700;
	color: #1a1a1a;
	font-family: "DM Mono", monospace;
}
.activity-meta {
	font-size: 0.72rem;
	color: #aaa;
	margin-top: 0.1rem;
}
.activity-status {
	font-size: 0.68rem;
	font-weight: 700;
	padding: 0.2rem 0.55rem;
	border-radius: 20px;
	white-space: nowrap;
	text-align: center;
}

/* Status Colors */
.st-draft {
	background: #f5f5f5;
	color: #888;
}
.st-pending {
	background: #fff3e0;
	color: #e65100;
}
.st-verified {
	background: #e3f2fd;
	color: #1565c0;
}
.st-dispatched {
	background: #f3e5f5;
	color: #6a1b9a;
}
.st-completed {
	background: #e8f5e9;
	color: #2e7d32;
}
.st-cancelled {
	background: #ffebee;
	color: #c62828;
}
.activity-indicator.st-draft {
	background: #bbb;
}
.activity-indicator.st-pending {
	background: #e65100;
}
.activity-indicator.st-verified {
	background: #1565c0;
}
.activity-indicator.st-dispatched {
	background: #6a1b9a;
}
.activity-indicator.st-completed {
	background: #2e7d32;
}
.activity-indicator.st-cancelled {
	background: #c62828;
}
</style>
