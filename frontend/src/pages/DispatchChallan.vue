<template>
	<div class="page">
		<header class="header">
			<button class="back-btn" @click="router.push('/dashboard')">← Back</button>
			<h2>{{ showForm ? "New Challan" : "Dispatch Challans" }}</h2>
			<button v-if="!showForm" class="new-btn" @click="openNewForm">+ New</button>
			<div v-else style="width: 60px"></div>
		</header>

		<!-- LIST VIEW -->
		<div v-if="!showForm" class="list">
			<div v-if="loading" class="empty-state">
				<div class="dot-pulse"><span></span><span></span><span></span></div>
			</div>
			<div v-else-if="challans.length === 0" class="empty-state">
				<div class="empty-icon">📋</div>
				<p class="empty-text">No challans yet</p>
				<button class="create-first-btn" @click="openNewForm">Create First Challan</button>
			</div>
			<div v-else class="challan-list">
				<div
					class="challan-card"
					v-for="c in challans"
					:key="c.name"
					@click="openDetail(c)"
				>
					<div class="card-accent" :class="getStatusClass(c.workflow_state)"></div>
					<div class="card-inner">
						<div class="card-top">
							<span class="challan-id">{{ c.name }}</span>
							<span :class="'badge ' + getStatusClass(c.workflow_state)">{{
								c.workflow_state || "Draft"
							}}</span>
						</div>
						<div class="card-details">
							<div class="detail-item">
								<span class="detail-icon">🚗</span>
								<span>{{ c.vehicle || "No Vehicle" }}</span>
							</div>
							<div class="detail-item">
								<span class="detail-icon">👤</span>
								<span>{{ c.driver || "No Driver" }}</span>
							</div>
						</div>
						<div class="card-footer">
							<span class="card-date">{{ formatDate(c.creation) }}</span>
							<span class="card-arrow">→</span>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- FORM VIEW -->
		<div v-if="showForm" class="form-view">
			<!-- BASIC DETAILS -->
			<div class="form-section">
				<div class="section-title">🚗 Basic Details</div>
				<div class="field-group">
					<label>Vehicle <span class="required">*</span></label>
					<select v-model="form.vehicle" class="field-input">
						<option value="">Select Vehicle</option>
						<template v-for="v in vehicles" :key="v.name">
							<option
								v-if="
									v.vehicle_status !== 'On Trip' &&
									v.vehicle_status !== 'Maintenance'
								"
								:value="v.name"
							>
								{{ v.vehicle_name ? v.vehicle_name + " - " + v.name : v.name }}
							</option>
						</template>
					</select>
				</div>
				<div class="field-group">
					<label>Driver <span class="required">*</span></label>

					<select v-model="form.driver" class="field-input">
						<option value="">Select Driver</option>
						<template v-for="d in drivers" :key="d.name">
							<option
								v-if="
									d.driver_status !== 'On Trip' &&
									d.driver_status !== 'Not Available'
								"
								:value="d.name"
							>
								{{ d.driver_name || d.name }}
							</option>
						</template>
					</select>
				</div>
				<div class="field-group">
					<label>Total Tiffins Sent <span class="required">*</span></label>
					<input
						v-model="form.total_tiffins_sent"
						type="number"
						class="field-input"
						placeholder="Enter total tiffins loaded in vehicle"
					/>
				</div>
			</div>

			<!-- BOARDED ITEMS — qty_per_person is EDITABLE -->
			<div class="form-section">
				<div class="section-header">
					<div class="section-title">📦 Boarded Items</div>
					<button class="add-btn" @click="addItem">+ Add</button>
				</div>
				<div v-if="form.boarded_items.length === 0" class="empty-table">
					No items added yet
				</div>
				<div class="compact-item" v-for="(item, i) in form.boarded_items" :key="i">
					<div class="compact-row">
						<select v-model="item.item_name" class="field-input flex-2">
							<option value="">Select Item</option>
							<option
								v-for="it in availableItems(i)"
								:key="it.name"
								:value="it.item_name"
							>
								{{ it.item_name }}
							</option>
						</select>
						<select v-model="item.unit" class="field-input flex-1">
							<option value="">Unit</option>
							<option value="Kg">Kg</option>
							<option value="Ltr.">Ltr.</option>
							<option value="Count">Count</option>
						</select>
						<!-- EDITABLE qty -->
						<input
							v-model="item.qty_per_person"
							class="field-input flex-1"
							type="number"
							placeholder="Qty"
						/>
						<button class="icon-remove-btn" @click="form.boarded_items.splice(i, 1)">
							✕
						</button>
					</div>
				</div>
			</div>

			<!-- CENTER LIST — delivered_qty is READONLY -->
			<div class="form-section">
				<div class="section-header">
					<div class="section-title">🏢 Center List</div>
					<button class="add-btn" @click="addCenter">+ Add</button>
				</div>
				<div v-if="form.center_list.length === 0" class="empty-table">
					No centers added yet
				</div>
				<div class="compact-item" v-for="(center, i) in form.center_list" :key="i">
					<div class="compact-row">
						<select v-model="center.name1" class="field-input flex-3">
							<option value="">Select Center</option>
							<option v-for="c in availableCenters(i)" :key="c.name" :value="c.name">
								{{ c.name }}
							</option>
						</select>
						<!-- READONLY qty -->
						<input
							v-model="center.delivered_qty"
							class="field-input flex-1 readonly-input"
							type="number"
							placeholder="Qty"
							readonly
						/>
						<button class="icon-remove-btn" @click="form.center_list.splice(i, 1)">
							✕
						</button>
					</div>
				</div>
			</div>

			<p v-if="saveError" class="error-msg">⚠️ {{ saveError }}</p>

			<div class="form-actions">
				<button class="cancel-btn" @click="showForm = false">Cancel</button>
				<button class="save-btn" @click="saveChallan" :disabled="saving">
					{{ saving ? "Saving..." : "💾 Save Challan" }}
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { apiGet, listUrl } from "../utils/api.js";

const router = useRouter();
const challans = ref([]);
const vehicles = ref([]);
const drivers = ref([]);
const items = ref([]);
const centers = ref([]);
const loading = ref(true);
const showForm = ref(false);
const saving = ref(false);
const saveError = ref("");

const form = ref({
	vehicle: "",
	driver: "",
	total_tiffins_sent: "",
	boarded_items: [],
	center_list: [],
});

function openNewForm() {
	form.value = {
		vehicle: "",
		driver: "",
		total_tiffins_sent: "",
		boarded_items: [],
		center_list: [],
	};
	saveError.value = "";
	showForm.value = true;
}

function addItem() {
	form.value.boarded_items.push({ item_name: "", unit: "", qty_per_person: "" });
}

function addCenter() {
	form.value.center_list.push({ name1: "", delivered_qty: "" });
}

// Returns available items for a specific row (excludes already selected in other rows)
function availableItems(currentIndex) {
	const selected = form.value.boarded_items
		.filter((_, i) => i !== currentIndex)
		.map((item) => item.item_name)
		.filter(Boolean);
	return items.value.filter((it) => !selected.includes(it.item_name));
}

// Returns available centers for a specific row (excludes already selected in other rows)
function availableCenters(currentIndex) {
	const selected = form.value.center_list
		.filter((_, i) => i !== currentIndex)
		.map((c) => c.name1)
		.filter(Boolean);
	return centers.value.filter((c) => !selected.includes(c.name));
}

function formatDate(d) {
	if (!d) return "";
	return new Date(d).toLocaleDateString("en-IN", {
		day: "2-digit",
		month: "short",
		year: "numeric",
	});
}

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

function openDetail(c) {
	router.push(`/challan/${c.name}`);
}

async function fetchData() {
	loading.value = true;
	try {
		const [challanRes, vehicleRes, driverRes, itemRes, centerRes] = await Promise.all([
			apiGet(
				listUrl("TSF Dispatch Challan", [
					"name",
					"vehicle",
					"driver",
					"workflow_state",
					"creation",
				]),
			),
			apiGet(listUrl("TSF Vehicle", ["name", "vehicle_name", "vehicle_status"])),
			apiGet(listUrl("TSF Driver", ["name", "driver_name", "driver_status"])),
			apiGet(listUrl("TSF Items", ["name", "item_name"])),
			apiGet(listUrl("TSF Centre", ["name"])),
		]);
		challans.value = challanRes.data || [];
		vehicles.value = vehicleRes.data || [];
		drivers.value = driverRes.data || [];
		items.value = itemRes.data || [];
		centers.value = centerRes.data || [];
	} catch (e) {
		console.error(e);
	}
	loading.value = false;
}

async function saveChallan() {
	// Guard: prevent double-save from multiple taps
	if (saving.value) return;

	const vehicle = (form.value.vehicle || "").trim();
	const driver = (form.value.driver || "").trim();
	const tiffins = parseInt(form.value.total_tiffins_sent) || 0;

	if (!vehicle || !driver) {
		saveError.value = "Please select both Vehicle and Driver.";
		return;
	}
	if (!tiffins || tiffins <= 0) {
		saveError.value = "Please enter Total Tiffins Sent.";
		return;
	}

	saving.value = true;
	saveError.value = "";

	try {
		// Using POST directly — apiMethod uses GET which causes issues with Frappe
		const res = await fetch("/api/method/intern_test.api.create_dispatch_challan", {
			method: "POST",
			credentials: "include",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
				"X-Frappe-CSRF-Token": "fetch",
				"X-Requested-With": "XMLHttpRequest",
			},
			body: JSON.stringify({
				vehicle,
				driver,
				total_tiffins_sent: parseInt(form.value.total_tiffins_sent) || 0,
				boarded_items: JSON.stringify(
					form.value.boarded_items.map((item) => ({
						item_name: item.item_name,
						unit: item.unit,
						qty_per_person: item.qty_per_person,
					})),
				),
				center_list: JSON.stringify(
					form.value.center_list.map((c) => ({
						name1: c.name1,
						delivered_qty: c.delivered_qty,
					})),
				),
			}),
		});

		const data = await res.json();

		if (data.message) {
			showForm.value = false;
			await fetchData();
		} else {
			saveError.value = "Failed to save. Please check all fields and try again.";
			console.error("Save error:", data);
		}
	} catch (e) {
		saveError.value = "Something went wrong. Please try again.";
		console.error("Save exception:", e);
	}

	saving.value = false;
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
	letter-spacing: -0.01em;
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
.new-btn {
	background: #2e7d32;
	border: none;
	color: white;
	padding: 0.4rem 0.9rem;
	border-radius: 20px;
	cursor: pointer;
	font-size: 0.82rem;
	font-weight: 700;
}
.list {
	padding: 1rem;
}
.challan-list {
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
	font-size: 0.9rem;
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
.create-first-btn {
	background: #2e7d32;
	color: white;
	border: none;
	padding: 0.75rem 1.75rem;
	border-radius: 25px;
	cursor: pointer;
	font-weight: 700;
	font-size: 0.9rem;
}
.challan-card {
	background: white;
	border-radius: 16px;
	overflow: hidden;
	box-shadow: 0 1px 4px rgba(0, 0, 0, 0.07);
	cursor: pointer;
	display: flex;
	transition:
		transform 0.15s,
		box-shadow 0.15s;
}
.challan-card:active {
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
	margin-bottom: 0.55rem;
}
.challan-id {
	font-weight: 700;
	font-size: 0.88rem;
	color: #1a1a1a;
	font-family: "DM Mono", monospace;
}
.card-details {
	display: flex;
	gap: 1rem;
	margin-bottom: 0.55rem;
}
.detail-item {
	display: flex;
	align-items: center;
	gap: 0.3rem;
	font-size: 0.8rem;
	color: #666;
}
.detail-icon {
	font-size: 0.9rem;
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
.card-arrow {
	font-size: 0.85rem;
	color: #ccc;
}
.badge {
	padding: 0.2rem 0.6rem;
	border-radius: 20px;
	font-size: 0.68rem;
	font-weight: 700;
}
.st-draft {
	background: #f0f0f0;
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
.card-accent.st-draft {
	background: #ddd;
}
.card-accent.st-pending {
	background: #e65100;
}
.card-accent.st-verified {
	background: #1565c0;
}
.card-accent.st-dispatched {
	background: #6a1b9a;
}
.card-accent.st-completed {
	background: #2e7d32;
}
.card-accent.st-cancelled {
	background: #c62828;
}
.form-view {
	padding: 1rem;
	display: flex;
	flex-direction: column;
	gap: 0.85rem;
}
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
	margin-bottom: 0.85rem;
}
.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 0.75rem;
}
.add-btn {
	background: #e8f5e9;
	color: #2e7d32;
	border: none;
	padding: 0.35rem 0.85rem;
	border-radius: 20px;
	cursor: pointer;
	font-size: 0.8rem;
	font-weight: 700;
}
.field-group {
	margin-bottom: 0.75rem;
}
label {
	display: block;
	font-size: 0.72rem;
	color: #888;
	font-weight: 700;
	margin-bottom: 0.3rem;
	text-transform: uppercase;
	letter-spacing: 0.04em;
}
.field-input {
	width: 100%;
	padding: 0.7rem 0.85rem;
	border: 1.5px solid #ebebeb;
	border-radius: 10px;
	font-size: 0.88rem;
	background: #fafafa;
	outline: none;
	transition:
		border 0.2s,
		background 0.2s;
}
.field-input:focus {
	border-color: #2e7d32;
	background: white;
}
.compact-item {
	margin-bottom: 0.5rem;
}
.compact-row {
	display: flex;
	gap: 0.4rem;
	align-items: center;
}
.flex-1 {
	flex: 1;
}
.flex-2 {
	flex: 2;
}
.flex-3 {
	flex: 3;
}
.compact-row .field-input {
	padding: 0.6rem 0.5rem;
	font-size: 0.82rem;
	min-width: 0;
}
.readonly-input {
	background: #f0f0f0;
	color: #888;
	cursor: not-allowed;
}
.icon-remove-btn {
	background: #ffebee;
	color: #c62828;
	border: none;
	border-radius: 8px;
	padding: 0.6rem;
	cursor: pointer;
	font-size: 0.8rem;
	flex-shrink: 0;
}
.empty-table {
	text-align: center;
	padding: 1.1rem;
	color: #ccc;
	font-size: 0.82rem;
	background: #fafafa;
	border-radius: 10px;
}
.form-actions {
	display: flex;
	gap: 0.65rem;
	padding-bottom: 0.5rem;
}
.cancel-btn {
	flex: 1;
	padding: 0.9rem;
	background: white;
	border: 1.5px solid #e8e8e8;
	border-radius: 14px;
	cursor: pointer;
	font-size: 0.92rem;
	color: #666;
	font-weight: 600;
}
.save-btn {
	flex: 2;
	padding: 0.9rem;
	background: #1a4a1e;
	color: white;
	border: none;
	border-radius: 14px;
	cursor: pointer;
	font-size: 0.92rem;
	font-weight: 700;
}
.save-btn:disabled {
	opacity: 0.6;
	pointer-events: none;
}
.required {
	color: #c62828;
}
.error-msg {
	color: #c62828;
	font-size: 0.82rem;
	background: #ffebee;
	padding: 0.75rem 1rem;
	border-radius: 10px;
}
</style>
