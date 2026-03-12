<template>
	<div class="page">
		<header class="header">
			<button class="back-btn" @click="router.push('/dashboard')">← Back</button>
			<h2>{{ showForm ? "Verify Vehicle" : "Security Checks" }}</h2>
			<div style="width: 60px"></div>
		</header>

		<!-- LIST VIEW -->
		<div v-if="!showForm">
			<div class="tabs">
				<button
					:class="['tab', activeTab === 'pending' ? 'tab-active' : '']"
					@click="activeTab = 'pending'"
				>
					Pending
					<span class="tab-count" v-if="pendingChecks.length > 0">{{
						pendingChecks.length
					}}</span>
				</button>
				<button
					:class="['tab', activeTab === 'all' ? 'tab-active' : '']"
					@click="activeTab = 'all'"
				>
					History
				</button>
			</div>

			<div class="list">
				<div v-if="loading" class="empty-state">
					<div class="dot-pulse"><span></span><span></span><span></span></div>
				</div>

				<!-- Pending -->
				<template v-else-if="activeTab === 'pending'">
					<div v-if="pendingChecks.length === 0" class="empty-state">
						<div class="empty-icon">✅</div>
						<p class="empty-text">All clear! No pending verifications</p>
					</div>
					<div
						class="check-card"
						v-else
						v-for="c in pendingChecks"
						:key="c.name"
						@click="openCheckForm(c)"
					>
						<div class="card-accent st-pending"></div>
						<div class="card-inner">
							<div class="card-top">
								<span class="card-id">{{ c.name }}</span>
								<span class="badge st-pending">Pending</span>
							</div>
							<div class="card-details">
								<div class="detail-item" v-if="c.challan_ref">
									📋 {{ c.challan_ref }}
								</div>
								<div class="detail-item" v-if="c.checkpoint">
									📍 {{ c.checkpoint }}
								</div>
								<div class="detail-item" v-if="c.counted_qty">
									📦 Qty: {{ c.counted_qty }}
								</div>
								<div class="detail-item" v-if="c.time">
									🕐 {{ formatDate(c.time) }}
								</div>
							</div>
							<div class="card-footer">
								<span class="card-date">{{ formatDate(c.creation) }}</span>
								<span class="tap-hint">Tap to verify →</span>
							</div>
						</div>
					</div>
				</template>

				<!-- History -->
				<template v-else>
					<div v-if="allChecks.length === 0" class="empty-state">
						<div class="empty-icon">🔒</div>
						<p class="empty-text">No history yet</p>
					</div>
					<div class="check-card" v-else v-for="c in allChecks" :key="c.name">
						<div :class="'card-accent ' + getStatusClass(c.workflow_state)"></div>
						<div class="card-inner">
							<div class="card-top">
								<span class="card-id">{{ c.name }}</span>
								<span :class="'badge ' + getStatusClass(c.workflow_state)">
									{{ getStatusLabel(c.workflow_state) }}
								</span>
							</div>
							<div class="card-details">
								<div class="detail-item" v-if="c.challan_ref">
									📋 {{ c.challan_ref }}
								</div>
								<div class="detail-item" v-if="c.checkpoint">
									📍 {{ c.checkpoint }}
								</div>
								<div class="detail-item" v-if="c.counted_qty">
									📦 Qty: {{ c.counted_qty }}
								</div>
							</div>
							<div class="card-footer">
								<span class="card-date">{{ formatDate(c.creation) }}</span>
								<span class="status-icon">{{
									getStatusIcon(c.workflow_state)
								}}</span>
							</div>
						</div>
					</div>
				</template>
			</div>
		</div>

		<!-- VERIFICATION FORM -->
		<div v-if="showForm" class="form-view">
			<!-- Preview -->
			<div class="challan-preview">
				<div class="preview-label">Security Check</div>
				<div class="preview-id">{{ selectedCheck.name }}</div>
				<div class="preview-divider"></div>
				<div class="preview-grid">
					<div class="preview-item">
						<span class="preview-key">Challan Ref</span>
						<span class="preview-val">{{ selectedCheck.challan_ref || "—" }}</span>
					</div>
					<div class="preview-item">
						<span class="preview-key">Expected Qty</span>
						<span class="preview-val">{{
							challanData.total_tiffins_sent ?? "—"
						}}</span>
					</div>
					<div class="preview-item">
						<span class="preview-key">Vehicle</span>
						<span class="preview-val">{{ challanData.vehicle || "—" }}</span>
					</div>
					<div class="preview-item">
						<span class="preview-key">Last Odometer</span>
						<span class="preview-val">
							{{
								vehicleLastOdo !== null
									? vehicleLastOdo + " km"
									: loadingChallan
										? "…"
										: "—"
							}}
						</span>
					</div>
				</div>
			</div>

			<!-- Loading challan data indicator -->
			<div v-if="loadingChallan" class="info-banner">
				<div class="dot-pulse sm"><span></span><span></span><span></span></div>
				<span>Fetching challan &amp; vehicle data…</span>
			</div>

			<!-- Progress Ring -->
			<div class="progress-section">
				<svg class="progress-ring" viewBox="0 0 80 80">
					<circle cx="40" cy="40" r="34" fill="none" stroke="#e8f5e9" stroke-width="7" />
					<circle
						cx="40"
						cy="40"
						r="34"
						fill="none"
						stroke="#2e7d32"
						stroke-width="7"
						stroke-dasharray="213.6"
						:stroke-dashoffset="213.6 - (213.6 * checkedCount) / 4"
						stroke-linecap="round"
						transform="rotate(-90 40 40)"
						style="transition: stroke-dashoffset 0.4s ease"
					/>
					<text
						x="40"
						y="44"
						text-anchor="middle"
						font-size="18"
						font-weight="700"
						fill="#1a4a1e"
						font-family="DM Mono"
					>
						{{ checkedCount }}/4
					</text>
				</svg>
				<div class="progress-info">
					<div class="progress-title">Verification Progress</div>
					<div class="progress-sub">
						{{
							checkedCount === 4
								? "✅ All checks passed"
								: `${4 - checkedCount} check${4 - checkedCount > 1 ? "s" : ""} remaining`
						}}
					</div>
				</div>
			</div>

			<!-- Checklist -->
			<div class="form-section">
				<div class="section-title">🔍 Verification Checklist</div>
				<div class="check-item" v-for="item in checklist" :key="item.key">
					<div class="check-info">
						<div class="check-label">{{ item.label }}</div>
						<div class="check-sub">{{ item.sub }}</div>
					</div>
					<label class="toggle">
						<input type="checkbox" v-model="checkForm[item.key]" />
						<span class="toggle-slider"></span>
					</label>
				</div>
			</div>

			<!-- Checkpoint -->
			<div class="form-section">
				<div class="section-title">📍 Checkpoint</div>
				<div class="segment-group">
					<button
						v-for="opt in ['Gate IN', 'Gate OUT']"
						:key="opt"
						:class="[
							'segment-btn',
							checkForm.checkpoint === opt ? 'segment-active' : '',
						]"
						@click="checkForm.checkpoint = opt"
					>
						{{ opt === "Gate IN" ? "🚪 Gate IN" : "🚦 Gate OUT" }}
					</button>
				</div>
				<p v-if="validationErrors.checkpoint" class="field-error">
					⚠️ {{ validationErrors.checkpoint }}
				</p>
			</div>

			<!-- Counted Qty -->
			<div class="form-section">
				<div class="section-title">📦 Counted Quantity</div>
				<div class="qty-wrap">
					<div class="qty-display">
						<div class="qty-guard-label">Guard Count</div>
						<input
							v-model.number="checkForm.counted_qty"
							type="number"
							min="0"
							class="field-input qty-input"
							placeholder="Enter counted qty"
						/>
					</div>
					<div class="qty-divider">vs</div>
					<div class="qty-expected">
						<div class="qty-expected-label">Challan Expected</div>
						<div class="qty-expected-val">
							{{ challanData.total_tiffins_sent ?? (loadingChallan ? "…" : "—") }}
						</div>
					</div>
				</div>
				<div
					v-if="checkForm.counted_qty !== '' && challanData.total_tiffins_sent !== null"
					:class="['qty-match-badge', qtyMatches ? 'qty-ok' : 'qty-fail']"
				>
					{{
						qtyMatches
							? "✅ Quantity matches challan"
							: "❌ Mismatch! Count must equal " + challanData.total_tiffins_sent
					}}
				</div>
				<p v-if="validationErrors.counted_qty" class="field-error">
					⚠️ {{ validationErrors.counted_qty }}
				</p>
			</div>

			<!-- Odometer -->
			<div class="form-section">
				<div class="section-title">🔢 Entered Odometer Reading</div>
				<div class="odo-wrap">
					<input
						v-model.number="checkForm.entered_odometer_reading"
						type="number"
						min="0"
						class="field-input odo-input"
						placeholder="Enter current odometer (km)"
					/>
					<span class="odo-unit">km</span>
				</div>
				<div class="odo-hint-row">
					<span class="odo-hint">Vehicle last recorded odometer:</span>
					<span class="odo-last-val">
						{{
							vehicleLastOdo !== null
								? vehicleLastOdo + " km"
								: loadingChallan
									? "…"
									: "N/A"
						}}
					</span>
				</div>
				<div
					v-if="checkForm.entered_odometer_reading !== '' && vehicleLastOdo !== null"
					:class="['odo-match-badge', odoValid ? 'qty-ok' : 'qty-fail']"
				>
					{{
						odoValid
							? "✅ Reading is valid (≥ last recorded)"
							: "❌ Must be ≥ " + vehicleLastOdo + " km (vehicle's last odometer)"
					}}
				</div>
				<p v-if="validationErrors.entered_odometer_reading" class="field-error">
					⚠️ {{ validationErrors.entered_odometer_reading }}
				</p>
			</div>

			<!-- Dispatch Time -->
			<div class="form-section">
				<div class="section-title">🕐 Dispatch Time</div>
				<div v-if="!checkForm.dispatch_time" class="time-unset">
					<div class="time-unset-icon">⏱️</div>
					<div class="time-unset-text">Dispatch time not recorded yet</div>
					<button class="record-time-btn" @click="recordDispatchTime">
						Record Time Now
					</button>
				</div>
				<div v-else class="time-recorded">
					<div class="time-recorded-top">
						<div class="time-recorded-val">
							{{ formatDispatchTime(checkForm.dispatch_time) }}
						</div>
						<button class="time-reset-btn" @click="checkForm.dispatch_time = ''">
							✕ Reset
						</button>
					</div>
					<div class="time-recorded-badge">✅ Time recorded</div>
				</div>
				<p v-if="validationErrors.dispatch_time" class="field-error">
					⚠️ {{ validationErrors.dispatch_time }}
				</p>
			</div>

			<!-- Remarks -->
			<div class="form-section">
				<div class="section-title">📝 Remarks</div>
				<textarea
					v-model="checkForm.remarks"
					class="field-input"
					rows="3"
					placeholder="Any observations or notes..."
				></textarea>
			</div>

			<p v-if="saveError" class="error-msg">⚠️ {{ saveError }}</p>
			<p v-if="saveSuccess" class="success-msg">✅ {{ saveSuccess }}</p>

			<!-- Actions -->
			<div class="form-actions">
				<button class="cancel-btn" @click="showForm = false">Cancel</button>
				<button class="reject-btn" @click="triggerAction('Reject')" :disabled="!!saving">
					{{ saving === "Reject" ? "..." : "❌ Reject" }}
				</button>
				<button
					class="verify-btn"
					@click="triggerAction('Verify')"
					:disabled="!!saving || !canDispatch"
				>
					{{ saving === "Verify" ? "Dispatching..." : "🚚 Dispatch" }}
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { apiGet, apiPut, listUrl } from "../utils/api.js";

const router = useRouter();
const loading = ref(true);
const loadingChallan = ref(false);
const showForm = ref(false);
const saving = ref(false);
const saveError = ref("");
const saveSuccess = ref("");
const activeTab = ref("pending");
const pendingChecks = ref([]);
const allChecks = ref([]);
const selectedCheck = ref({});

// Data fetched from linked doctypes
const challanData = ref({ total_tiffins_sent: null, vehicle: null });
const vehicleLastOdo = ref(null);

const checkForm = ref({
	vehicle_verified: false,
	driver_verified: false,
	items_verified: false,
	vehicle_condition_ok: false,
	checkpoint: "",
	counted_qty: "",
	entered_odometer_reading: "",
	dispatch_time: "",
	remarks: "",
});

const validationErrors = ref({});

const checklist = [
	{
		key: "vehicle_verified",
		label: "Vehicle Number Matches",
		sub: "Physical vehicle matches challan",
	},
	{
		key: "driver_verified",
		label: "Driver Identity Verified",
		sub: "License matches driver on record",
	},
	{
		key: "items_verified",
		label: "Items Count Matches",
		sub: "Loaded items match challan quantity",
	},
	{
		key: "vehicle_condition_ok",
		label: "Vehicle Condition OK",
		sub: "No visible damage or issues",
	},
];

const checkedCount = computed(() => checklist.filter((item) => checkForm.value[item.key]).length);
const allVerified = computed(() => checkedCount.value === 4);

const qtyMatches = computed(() => {
	const expected = challanData.value.total_tiffins_sent;
	const entered = checkForm.value.counted_qty;
	if (entered === "" || expected === null) return null;
	return Number(entered) === Number(expected);
});

const odoValid = computed(() => {
	const last = vehicleLastOdo.value;
	const entered = checkForm.value.entered_odometer_reading;
	if (entered === "" || last === null) return null;
	return Number(entered) >= Number(last);
});

const canDispatch = computed(() => {
	return (
		allVerified.value &&
		checkForm.value.checkpoint &&
		qtyMatches.value === true &&
		odoValid.value === true &&
		!!checkForm.value.dispatch_time
	);
});

function formatDate(d) {
	if (!d) return "";
	return new Date(d).toLocaleDateString("en-IN", {
		day: "2-digit",
		month: "short",
		year: "numeric",
	});
}

function formatDispatchTime(isoString) {
	if (!isoString) return "—";
	return new Date(isoString).toLocaleString("en-IN", {
		day: "2-digit",
		month: "short",
		year: "numeric",
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit",
		hour12: true,
	});
}

function recordDispatchTime() {
	checkForm.value.dispatch_time = new Date().toISOString();
}

function getStatusClass(status) {
	const map = {
		Pending: "st-pending",
		Verified: "st-verified",
		Dispatched: "st-dispatched",
		Rejected: "st-rejected",
	};
	return map[status] || "st-pending";
}

function getStatusLabel(status) {
	const map = {
		Pending: "Pending",
		Verified: "Verified",
		Dispatched: "Dispatched ✓",
		Rejected: "Rejected",
	};
	return map[status] || status || "Pending";
}

function getStatusIcon(status) {
	const map = { Pending: "⏳", Verified: "✅", Dispatched: "🚚", Rejected: "❌" };
	return map[status] || "⏳";
}

async function fetchChallanAndVehicle(challanRef) {
	if (!challanRef) return;
	loadingChallan.value = true;
	challanData.value = { total_tiffins_sent: null, vehicle: null };
	vehicleLastOdo.value = null;

	try {
		const challanRes = await apiGet(
			`/api/resource/TSF Dispatch Challan/${challanRef}?fields=["total_tiffins_sent","vehicle"]`,
		);
		const cd = challanRes.data || {};
		challanData.value = {
			total_tiffins_sent: cd.total_tiffins_sent ?? null,
			vehicle: cd.vehicle || null,
		};

		if (cd.total_tiffins_sent !== null && cd.total_tiffins_sent !== undefined) {
			checkForm.value.counted_qty = cd.total_tiffins_sent;
		}

		if (cd.vehicle) {
			const vehicleRes = await apiGet(
				`/api/resource/TSF Vehicle/${cd.vehicle}?fields=["last_odometer_reading"]`,
			);
			const vd = vehicleRes.data || {};
			vehicleLastOdo.value = vd.last_odometer_reading ?? null;
		}
	} catch (e) {
		console.error("fetchChallanAndVehicle error:", e);
	}

	loadingChallan.value = false;
}

function openCheckForm(check) {
	selectedCheck.value = check;
	checkForm.value = {
		vehicle_verified: false,
		driver_verified: false,
		items_verified: false,
		vehicle_condition_ok: false,
		checkpoint: "",
		counted_qty: "",
		entered_odometer_reading: "",
		dispatch_time: "",
		remarks: "",
	};
	validationErrors.value = {};
	saveError.value = "";
	saveSuccess.value = "";
	showForm.value = true;

	fetchChallanAndVehicle(check.challan_ref);
}

async function fetchData() {
	loading.value = true;
	try {
		const fields = [
			"name",
			"challan_ref",
			"checkpoint",
			"counted_qty",
			"time",
			"entered_odometer_reading",
			"workflow_state",
			"creation",
		];
		const allRes = await apiGet(listUrl("TSF Security Check", fields, [], 50));
		const all = allRes.data || [];
		allChecks.value = all;
		pendingChecks.value = all.filter((c) => {
			const state = (c.workflow_state || "").trim();
			return state === "" || state === "Pending";
		});
	} catch (e) {
		console.error("fetchData error:", e);
	}
	loading.value = false;
}

function validate(action) {
	const errors = {};

	if (action === "Verify") {
		if (!checkForm.value.checkpoint) {
			errors.checkpoint = "Please select a checkpoint (Gate IN or Gate OUT).";
		}

		const expected = challanData.value.total_tiffins_sent;
		if (checkForm.value.counted_qty === "" || checkForm.value.counted_qty === null) {
			errors.counted_qty = "Please enter the counted quantity.";
		} else if (expected !== null && Number(checkForm.value.counted_qty) !== Number(expected)) {
			errors.counted_qty = `Counted qty (${checkForm.value.counted_qty}) must equal challan qty (${expected}).`;
		}

		const lastOdo = vehicleLastOdo.value;
		if (
			checkForm.value.entered_odometer_reading === "" ||
			checkForm.value.entered_odometer_reading === null
		) {
			errors.entered_odometer_reading = "Please enter the odometer reading.";
		} else if (
			lastOdo !== null &&
			Number(checkForm.value.entered_odometer_reading) < Number(lastOdo)
		) {
			errors.entered_odometer_reading = `Odometer (${checkForm.value.entered_odometer_reading} km) must be ≥ vehicle's last reading (${lastOdo} km).`;
		}

		if (!checkForm.value.dispatch_time) {
			errors.dispatch_time = "Please record the dispatch time before submitting.";
		}
	}

	validationErrors.value = errors;
	return Object.keys(errors).length === 0;
}

async function triggerAction(action) {
	if (!validate(action)) return;

	saving.value = action;
	saveError.value = "";
	saveSuccess.value = "";

	try {
		const newState = action === "Verify" ? "Dispatched" : "Rejected";

		const res = await apiPut(`/api/resource/TSF Security Check/${selectedCheck.value.name}`, {
			vehicle_verified: checkForm.value.vehicle_verified ? 1 : 0,
			driver_verified: checkForm.value.driver_verified ? 1 : 0,
			items_verified: checkForm.value.items_verified ? 1 : 0,
			vehicle_condition_ok: checkForm.value.vehicle_condition_ok ? 1 : 0,
			checkpoint: checkForm.value.checkpoint,
			counted_qty: checkForm.value.counted_qty,
			entered_odometer_reading: parseInt(checkForm.value.entered_odometer_reading) || 0,
			dispatch_time: action === "Verify" ? checkForm.value.dispatch_time : null,
			remarks: checkForm.value.remarks,
			workflow_state: newState,
		});

		if (!res.data) {
			saveError.value = "Action failed. Check your role permissions.";
		} else {
			saveSuccess.value =
				action === "Verify" ? "Vehicle verified & dispatched! 🚚" : "Check rejected.";
			setTimeout(() => {
				showForm.value = false;
				fetchData();
			}, 1500);
		}
	} catch (e) {
		saveError.value = e.message;
	} finally {
		saving.value = false;
	}
}

onMounted(fetchData);
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@500&display=swap");
* {
	font-family: "DM Sans", sans-serif;
}
.page {
	min-height: 100vh;
	background: #f4f6f4;
	padding-bottom: 2rem;
}
.header {
	background: #1a4a1e;
	color: white;
	padding: 1rem 1.1rem;
	display: flex;
	justify-content: space-between;
	align-items: center;
	position: sticky;
	top: 0;
	z-index: 10;
}
.header h2 {
	font-size: 1rem;
	font-weight: 700;
}
.back-btn {
	background: rgba(255, 255, 255, 0.1);
	border: 1px solid rgba(255, 255, 255, 0.2);
	color: white;
	padding: 0.4rem 0.75rem;
	border-radius: 20px;
	cursor: pointer;
	font-size: 0.82rem;
}
.tabs {
	display: flex;
	background: white;
	border-bottom: 2px solid #f0f0f0;
}
.tab {
	flex: 1;
	padding: 0.85rem;
	border: none;
	background: transparent;
	font-size: 0.88rem;
	color: #aaa;
	cursor: pointer;
	font-weight: 600;
	transition: color 0.2s;
}
.tab-active {
	color: #2e7d32;
	border-bottom: 2.5px solid #2e7d32;
	margin-bottom: -2px;
}
.tab-count {
	background: #e65100;
	color: white;
	border-radius: 20px;
	padding: 0.1rem 0.5rem;
	font-size: 0.7rem;
	margin-left: 0.35rem;
}
.list {
	padding: 1rem;
	display: flex;
	flex-direction: column;
	gap: 0.65rem;
}
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 4rem 1rem;
	gap: 0.75rem;
}
.empty-icon {
	font-size: 3rem;
}
.empty-text {
	color: #aaa;
	font-size: 0.88rem;
}
.dot-pulse {
	display: flex;
	gap: 0.4rem;
}
.dot-pulse span {
	width: 9px;
	height: 9px;
	background: #2e7d32;
	border-radius: 50%;
	animation: pulse 1.2s ease-in-out infinite;
}
.dot-pulse.sm span {
	width: 6px;
	height: 6px;
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
.check-card {
	background: white;
	border-radius: 16px;
	overflow: hidden;
	box-shadow: 0 1px 4px rgba(0, 0, 0, 0.07);
	cursor: pointer;
	display: flex;
	transition: transform 0.15s;
}
.check-card:active {
	transform: scale(0.98);
}
.card-accent {
	width: 4px;
	flex-shrink: 0;
}
.card-inner {
	flex: 1;
	padding: 0.9rem 1rem;
}
.card-top {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 0.5rem;
}
.card-id {
	font-weight: 700;
	font-size: 0.88rem;
	color: #1a1a1a;
	font-family: "DM Mono", monospace;
}
.card-details {
	display: flex;
	flex-wrap: wrap;
	gap: 0.5rem 1rem;
	margin-bottom: 0.5rem;
}
.detail-item {
	font-size: 0.8rem;
	color: #666;
}
.card-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
}
.card-date {
	font-size: 0.72rem;
	color: #bbb;
	font-family: "DM Mono", monospace;
}
.tap-hint {
	font-size: 0.72rem;
	color: #2e7d32;
	font-weight: 700;
}
.status-icon {
	font-size: 0.9rem;
}
.badge {
	padding: 0.2rem 0.6rem;
	border-radius: 20px;
	font-size: 0.68rem;
	font-weight: 700;
}
.st-pending {
	background: #fff3e0;
	color: #e65100;
}
.st-verified {
	background: #e8f5e9;
	color: #2e7d32;
}
.st-rejected {
	background: #ffebee;
	color: #c62828;
}
.st-dispatched {
	background: #e3f2fd;
	color: #1565c0;
}
.card-accent.st-pending {
	background: #e65100;
}
.card-accent.st-verified {
	background: #2e7d32;
}
.card-accent.st-rejected {
	background: #c62828;
}
.card-accent.st-dispatched {
	background: #1565c0;
}

/* Form */
.form-view {
	padding: 1rem;
	display: flex;
	flex-direction: column;
	gap: 0.85rem;
}
.challan-preview {
	background: #1a4a1e;
	border-radius: 16px;
	padding: 1.1rem;
}
.preview-label {
	font-size: 0.68rem;
	color: rgba(255, 255, 255, 0.5);
	text-transform: uppercase;
	letter-spacing: 0.06em;
	margin-bottom: 0.3rem;
}
.preview-id {
	font-size: 1.1rem;
	font-weight: 700;
	color: white;
	font-family: "DM Mono", monospace;
	margin-bottom: 0.85rem;
}
.preview-divider {
	height: 1px;
	background: rgba(255, 255, 255, 0.12);
	margin-bottom: 0.85rem;
}
.preview-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 0.5rem;
}
.preview-item {
	display: flex;
	flex-direction: column;
	gap: 0.15rem;
}
.preview-key {
	font-size: 0.65rem;
	color: rgba(255, 255, 255, 0.45);
	text-transform: uppercase;
	letter-spacing: 0.05em;
}
.preview-val {
	font-size: 0.82rem;
	color: rgba(255, 255, 255, 0.9);
	font-weight: 600;
}

/* Info banner */
.info-banner {
	background: #e8f5e9;
	border-radius: 12px;
	padding: 0.75rem 1rem;
	display: flex;
	align-items: center;
	gap: 0.75rem;
	font-size: 0.82rem;
	color: #2e7d32;
	font-weight: 600;
}

/* Progress Ring */
.progress-section {
	background: white;
	border-radius: 16px;
	padding: 1rem;
	display: flex;
	align-items: center;
	gap: 1rem;
	box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.progress-ring {
	width: 80px;
	height: 80px;
	flex-shrink: 0;
}
.progress-title {
	font-size: 0.9rem;
	font-weight: 700;
	color: #1a1a1a;
	margin-bottom: 0.25rem;
}
.progress-sub {
	font-size: 0.8rem;
	color: #888;
}

/* Checklist */
.form-section {
	background: white;
	border-radius: 16px;
	padding: 1rem;
	box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.section-title {
	font-size: 0.85rem;
	font-weight: 700;
	color: #2e7d32;
	margin-bottom: 0.75rem;
}
.check-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 0.8rem 0;
	border-bottom: 1px solid #f5f5f5;
}
.check-item:last-child {
	border-bottom: none;
	padding-bottom: 0;
}
.check-info {
	flex: 1;
}
.check-label {
	font-size: 0.88rem;
	font-weight: 600;
	color: #1a1a1a;
}
.check-sub {
	font-size: 0.73rem;
	color: #aaa;
	margin-top: 0.15rem;
}
.toggle {
	position: relative;
	display: inline-block;
	width: 48px;
	height: 26px;
	flex-shrink: 0;
}
.toggle input {
	opacity: 0;
	width: 0;
	height: 0;
}
.toggle-slider {
	position: absolute;
	cursor: pointer;
	inset: 0;
	background: #e0e0e0;
	border-radius: 26px;
	transition: 0.3s;
}
.toggle-slider:before {
	position: absolute;
	content: "";
	height: 20px;
	width: 20px;
	left: 3px;
	bottom: 3px;
	background: white;
	border-radius: 50%;
	transition: 0.3s;
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}
input:checked + .toggle-slider {
	background: #2e7d32;
}
input:checked + .toggle-slider:before {
	transform: translateX(22px);
}

/* Checkpoint Segment */
.segment-group {
	display: flex;
	gap: 0.6rem;
}
.segment-btn {
	flex: 1;
	padding: 0.75rem;
	border: 2px solid #e8e8e8;
	border-radius: 12px;
	background: #fafafa;
	font-size: 0.88rem;
	font-weight: 600;
	color: #888;
	cursor: pointer;
	transition: all 0.2s;
}
.segment-active {
	border-color: #2e7d32;
	background: #e8f5e9;
	color: #2e7d32;
}

/* Qty */
.qty-wrap {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	margin-bottom: 0.6rem;
}
.qty-display {
	flex: 1;
}
.qty-guard-label {
	font-size: 0.7rem;
	color: #aaa;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.04em;
	margin-bottom: 0.3rem;
}
.qty-input {
	font-size: 1.1rem;
	font-weight: 700;
	font-family: "DM Mono", monospace;
}
.qty-divider {
	font-size: 0.75rem;
	font-weight: 700;
	color: #bbb;
	flex-shrink: 0;
}
.qty-expected {
	text-align: center;
	flex-shrink: 0;
}
.qty-expected-label {
	font-size: 0.65rem;
	color: #aaa;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.04em;
	margin-bottom: 0.3rem;
}
.qty-expected-val {
	font-size: 1.4rem;
	font-weight: 700;
	color: #1a4a1e;
	font-family: "DM Mono", monospace;
}
.qty-match-badge,
.odo-match-badge {
	padding: 0.5rem 0.75rem;
	border-radius: 10px;
	font-size: 0.8rem;
	font-weight: 700;
	margin-top: 0.4rem;
}
.qty-ok {
	background: #e8f5e9;
	color: #2e7d32;
}
.qty-fail {
	background: #ffebee;
	color: #c62828;
}

/* Odometer */
.odo-wrap {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	margin-bottom: 0.4rem;
}
.odo-input {
	flex: 1;
	font-size: 1rem;
	font-weight: 700;
	font-family: "DM Mono", monospace;
}
.odo-unit {
	font-size: 0.88rem;
	font-weight: 700;
	color: #2e7d32;
	flex-shrink: 0;
}
.odo-hint-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 0.3rem;
}
.odo-hint {
	font-size: 0.72rem;
	color: #bbb;
}
.odo-last-val {
	font-size: 0.78rem;
	font-weight: 700;
	color: #1a4a1e;
	font-family: "DM Mono", monospace;
}

/* Dispatch Time */
.time-unset {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 0.65rem;
	padding: 1rem 0 0.25rem;
}
.time-unset-icon {
	font-size: 2.2rem;
}
.time-unset-text {
	font-size: 0.82rem;
	color: #aaa;
	font-weight: 500;
}
.record-time-btn {
	background: #1a4a1e;
	color: white;
	border: none;
	border-radius: 12px;
	padding: 0.78rem 1.75rem;
	font-size: 0.9rem;
	font-weight: 700;
	cursor: pointer;
	letter-spacing: 0.02em;
	transition: opacity 0.2s;
	font-family: "DM Sans", sans-serif;
}
.record-time-btn:active {
	opacity: 0.8;
}
.time-recorded {
	display: flex;
	flex-direction: column;
	gap: 0.5rem;
}
.time-recorded-top {
	display: flex;
	align-items: center;
	justify-content: space-between;
	background: #f4f6f4;
	border-radius: 10px;
	padding: 0.75rem 1rem;
}
.time-recorded-val {
	font-size: 0.9rem;
	font-weight: 700;
	color: #1a4a1e;
	font-family: "DM Mono", monospace;
}
.time-reset-btn {
	background: #ffebee;
	color: #c62828;
	border: none;
	border-radius: 8px;
	padding: 0.3rem 0.65rem;
	font-size: 0.75rem;
	font-weight: 700;
	cursor: pointer;
	font-family: "DM Sans", sans-serif;
}
.time-recorded-badge {
	background: #e8f5e9;
	color: #2e7d32;
	border-radius: 10px;
	padding: 0.45rem 0.75rem;
	font-size: 0.8rem;
	font-weight: 700;
}

/* Inputs */
.field-input {
	width: 100%;
	padding: 0.7rem 0.85rem;
	border: 1.5px solid #ebebeb;
	border-radius: 10px;
	font-size: 0.88rem;
	background: #fafafa;
	outline: none;
	resize: none;
	transition: border 0.2s;
	font-family: "DM Sans", sans-serif;
	box-sizing: border-box;
}
.field-input:focus {
	border-color: #2e7d32;
	background: white;
}
.field-error {
	color: #c62828;
	font-size: 0.78rem;
	margin-top: 0.35rem;
	font-weight: 600;
}

/* Actions */
.form-actions {
	display: flex;
	gap: 0.6rem;
	padding-bottom: 0.5rem;
}
.cancel-btn {
	flex: 1;
	padding: 0.88rem;
	background: white;
	border: 1.5px solid #e8e8e8;
	border-radius: 14px;
	cursor: pointer;
	font-size: 0.88rem;
	color: #666;
	font-weight: 600;
}
.reject-btn {
	flex: 1;
	padding: 0.88rem;
	background: #ffebee;
	color: #c62828;
	border: none;
	border-radius: 14px;
	cursor: pointer;
	font-size: 0.88rem;
	font-weight: 700;
}
.verify-btn {
	flex: 2;
	padding: 0.88rem;
	background: #1a4a1e;
	color: white;
	border: none;
	border-radius: 14px;
	cursor: pointer;
	font-size: 0.88rem;
	font-weight: 700;
}
.verify-btn:disabled,
.reject-btn:disabled {
	opacity: 0.45;
}
.error-msg {
	color: #c62828;
	font-size: 0.82rem;
	background: #ffebee;
	padding: 0.75rem 1rem;
	border-radius: 10px;
}
.success-msg {
	color: #2e7d32;
	font-size: 0.82rem;
	background: #e8f5e9;
	padding: 0.75rem 1rem;
	border-radius: 10px;
}
</style>
