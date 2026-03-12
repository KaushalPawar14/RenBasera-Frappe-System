<template>
  <div class="page">
    <header class="header">
      <button class="back-btn" @click="router.push('/challan')">← Back</button>
      <h2>Challan Detail</h2>
      <div style="width: 60px"></div>
    </header>

    <div v-if="loading" class="empty-state">
      <div class="dot-pulse"><span></span><span></span><span></span></div>
    </div>

    <div v-else>
      <!-- Hero Status -->
      <div :class="'status-hero ' + getStatusClass(challan.workflow_state)">
        <div class="hero-bg-pattern"></div>
        <div class="hero-inner">
          <div class="hero-id">{{ challan.name }}</div>
          <div class="hero-state">{{ challan.workflow_state || 'Draft' }}</div>
          <div class="hero-date">Created {{ formatDate(challan.creation) }}</div>
        </div>
      </div>

      <!-- Info Cards Row -->
      <div class="info-row">
        <div class="info-pill">
          <span class="info-pill-icon">🚗</span>
          <div>
            <div class="info-pill-label">Vehicle</div>
            <div class="info-pill-val">{{ challan.vehicle || '—' }}</div>
          </div>
        </div>
        <div class="info-pill">
          <span class="info-pill-icon">👤</span>
          <div>
            <div class="info-pill-label">Driver</div>
            <div class="info-pill-val">{{ challan.driver || '—' }}</div>
          </div>
        </div>
      </div>

      <!-- Boarded Items -->
      <div class="section">
        <div class="section-title">📦 Boarded Items</div>
        <div
          v-if="!challan.boarded_items || challan.boarded_items.length === 0"
          class="empty-table"
        >
          No items
        </div>
        <div v-else class="data-table">
          <div class="table-head">
            <span class="col-lg">Item</span>
            <span class="col-sm">Unit</span>
            <span class="col-sm">Qty</span>
          </div>
          <div class="table-row" v-for="(item, i) in challan.boarded_items" :key="i">
            <span class="col-lg item-name">{{ item.item_name }}</span>
            <span class="col-sm">{{ item.unit }}</span>
            <span class="col-sm qty">{{ item.qty_per_person }}</span>
          </div>
        </div>
      </div>

      <!-- Center List -->
      <div class="section">
        <div class="section-title">🏢 Center List</div>
        <div v-if="!challan.center_list || challan.center_list.length === 0" class="empty-table">
          No centers
        </div>
        <div v-else class="data-table">
          <div class="table-head">
            <span class="col-lg">Center</span>
            <span class="col-sm">Qty</span>
          </div>
          <div class="table-row" v-for="(center, i) in challan.center_list" :key="i">
            <span class="col-lg item-name">{{ center.name1 || center.center_name || '—' }}</span>
            <span class="col-sm qty">{{ center.delivered_qty }}</span>
          </div>
        </div>
      </div>

      <!-- Workflow Actions -->
      <div class="section" v-if="availableActions.length > 0">
        <div class="section-title">⚡ Actions</div>
        <div class="actions-list">
          <button
            v-for="action in availableActions"
            :key="action.label"
            :class="'action-btn btn-' + action.style"
            @click="triggerAction(action)"
            :disabled="!!actionLoading"
          >
            <span class="action-btn-icon">{{ action.icon }}</span>
            <span class="action-btn-text">
              <span class="action-btn-label">{{
                actionLoading === action.label ? 'Processing...' : action.label
              }}</span>
              <span class="action-btn-sub">{{ action.desc }}</span>
            </span>
            <span class="action-btn-arrow">→</span>
          </button>
        </div>
        <p v-if="actionError" class="error-msg">⚠️ {{ actionError }}</p>
        <p v-if="actionSuccess" class="success-msg">✅ {{ actionSuccess }}</p>
      </div>

      <div class="section" v-else>
        <div class="section-title">⚡ Actions</div>
        <div class="no-action">
          <span v-if="challan.workflow_state === 'Completed'">🏁 This challan is completed.</span>
          <span v-else-if="challan.workflow_state === 'Cancelled'"
            >❌ This challan is cancelled.</span
          >
          <span v-else>No actions available for your role at this stage.</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../utils/api.js';
import { useAuthStore } from '../composables/useAuth';

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const loading = ref(true);
const actionLoading = ref(false);
const actionError = ref('');
const actionSuccess = ref('');
const challan = ref({});

function formatDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function getStatusClass(status) {
  // ... (Keep your existing getStatusClass map) ...
}

const availableActions = computed(() => {
  // ... (Keep your existing availableActions logic) ...
});

async function triggerAction(action) {
  actionLoading.value = action.label;
  actionError.value = '';
  actionSuccess.value = '';
  try {
    // Correct way to transition Workflows in Frappe
    const res = await api.post('/api/method/frappe.model.workflow.apply_workflow', {
      doc: { doctype: 'TSF Dispatch Challan', name: challan.value.name },
      action: action.workflow_action,
    });

    // Example of a standard PUT request if you were updating a field instead of a workflow:
    // await api.put(`/api/resource/TSF Dispatch Challan/${challan.value.name}`, {
    //     driver_name: "New Driver"
    // });

    if (res.data && res.data.exc) {
      actionError.value = 'Action failed. Check your role permissions.';
    } else {
      actionSuccess.value = `"${action.label}" completed successfully!`;
      await fetchChallan();
    }
  } catch (e) {
    actionError.value = e.response?.data?.exception || e.message;
  } finally {
    actionLoading.value = false;
  }
}

async function fetchChallan() {
  loading.value = true;
  try {
    // Standard Frappe Resource GET
    const res = await api.get(`/api/resource/TSF Dispatch Challan/${route.params.name}`);
    challan.value = res.data.data || {};
  } catch (e) {
    console.error('Failed to fetch Challan:', e);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchChallan);
</script>
<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@500&display=swap');
* {
  font-family: 'DM Sans', sans-serif;
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

.empty-state {
  display: flex;
  justify-content: center;
  padding: 4rem;
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

/* Status Hero */
.status-hero {
  position: relative;
  overflow: hidden;
  padding: 1.5rem 1.25rem;
}
.hero-bg-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.08;
  background-image: radial-gradient(circle, currentColor 1px, transparent 1px);
  background-size: 20px 20px;
}
.hero-inner {
  position: relative;
}
.hero-id {
  font-size: 1.3rem;
  font-weight: 700;
  font-family: 'DM Mono', monospace;
  margin-bottom: 0.3rem;
}
.hero-state {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.8;
  margin-bottom: 0.2rem;
}
.hero-date {
  font-size: 0.72rem;
  opacity: 0.6;
}
.hero-draft {
  background: #f5f5f5;
  color: #555;
}
.hero-pending {
  background: #fff3e0;
  color: #e65100;
}
.hero-verified {
  background: #e3f2fd;
  color: #1565c0;
}
.hero-dispatched {
  background: #f3e5f5;
  color: #6a1b9a;
}
.hero-completed {
  background: #e8f5e9;
  color: #2e7d32;
}
.hero-cancelled {
  background: #ffebee;
  color: #c62828;
}

/* Info Row */
.info-row {
  display: flex;
  gap: 0.65rem;
  padding: 0.85rem 1rem;
}
.info-pill {
  flex: 1;
  background: white;
  border-radius: 14px;
  padding: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.info-pill-icon {
  font-size: 1.3rem;
  flex-shrink: 0;
}
.info-pill-label {
  font-size: 0.65rem;
  color: #aaa;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.info-pill-val {
  font-size: 0.82rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-top: 0.1rem;
}

/* Sections */
.section {
  background: white;
  border-radius: 16px;
  margin: 0 1rem 0.85rem;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.section-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #2e7d32;
  margin-bottom: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* Table */
.data-table {
  border-radius: 10px;
  overflow: hidden;
  border: 1.5px solid #f0f0f0;
}
.table-head {
  display: flex;
  background: #f8f8f8;
  padding: 0.5rem 0.75rem;
}
.table-head span {
  font-size: 0.68rem;
  font-weight: 700;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.table-row {
  display: flex;
  padding: 0.65rem 0.75rem;
  border-top: 1px solid #f5f5f5;
  align-items: center;
}
.col-lg {
  flex: 3;
}
.col-sm {
  flex: 1;
  text-align: right;
}
.item-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1a1a1a;
}
.qty {
  font-size: 0.85rem;
  font-weight: 700;
  color: #2e7d32;
  font-family: 'DM Mono', monospace;
}
.empty-table {
  text-align: center;
  padding: 1.25rem;
  color: #ccc;
  font-size: 0.82rem;
}

/* Actions */
.actions-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.action-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.9rem 1rem;
  border: none;
  border-radius: 14px;
  cursor: pointer;
  text-align: left;
  transition:
    transform 0.15s,
    opacity 0.15s;
}
.action-btn:active {
  transform: scale(0.98);
}
.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.action-btn-icon {
  font-size: 1.4rem;
  flex-shrink: 0;
}
.action-btn-text {
  flex: 1;
}
.action-btn-label {
  display: block;
  font-size: 0.9rem;
  font-weight: 700;
}
.action-btn-sub {
  display: block;
  font-size: 0.72rem;
  opacity: 0.7;
  margin-top: 0.1rem;
}
.action-btn-arrow {
  font-size: 1rem;
  opacity: 0.5;
}
.btn-warning {
  background: #fff3e0;
  color: #e65100;
}
.btn-danger {
  background: #ffebee;
  color: #c62828;
}
.btn-primary {
  background: #f3e5f5;
  color: #6a1b9a;
}
.btn-success {
  background: #e8f5e9;
  color: #2e7d32;
}
.no-action {
  text-align: center;
  padding: 1.25rem;
  color: #bbb;
  font-size: 0.85rem;
}
.error-msg {
  color: #c62828;
  font-size: 0.82rem;
  background: #ffebee;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  margin-top: 0.75rem;
}
.success-msg {
  color: #2e7d32;
  font-size: 0.82rem;
  background: #e8f5e9;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  margin-top: 0.75rem;
}
</style>
