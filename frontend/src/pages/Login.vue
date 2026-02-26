<template>
  <div class="page">
    <div class="bg-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <div class="content">
      <div class="brand">
        <div class="brand-icon">🍱</div>
        <div class="brand-name">TSF Distribution</div>
        <div class="brand-sub">Tiffin Distribution Management</div>
      </div>

      <div class="card">
        <div class="card-title">Welcome back</div>
        <div class="card-sub">Sign in to continue</div>

        <div class="field-group">
          <label>Email</label>
          <div class="input-wrap" :class="{ focused: focusedField === 'email' }">
            <span class="input-icon">✉️</span>
            <input
              v-model="usr"
              type="email"
              placeholder="your@email.com"
              @focus="focusedField = 'email'"
              @blur="focusedField = ''"
              @keyup.enter="handleLogin"
            />
          </div>
        </div>

        <div class="field-group">
          <label>Password</label>
          <div class="input-wrap" :class="{ focused: focusedField === 'password' }">
            <span class="input-icon">🔑</span>
            <input
              v-model="pwd"
              :type="showPassword ? 'text' : 'password'"
              placeholder="••••••••"
              @focus="focusedField = 'password'"
              @blur="focusedField = ''"
              @keyup.enter="handleLogin"
            />
            <button class="toggle-pw" @click="showPassword = !showPassword" tabindex="-1">
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <div class="remember-row">
          <label class="remember-label">
            <input type="checkbox" v-model="rememberMe" class="remember-check" />
            <span>Remember me</span>
          </label>
        </div>

        <div v-if="error" class="error-msg">
          <span>⚠️</span> {{ error }}
        </div>

        <button class="login-btn" @click="handleLogin" :disabled="loading">
          <span v-if="loading" class="btn-spinner"></span>
          <span v-else>Sign In →</span>
        </button>
      </div>

      <div class="footer">TSF Distribution · Powered by Frappe</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../composables/useAuth'

const router = useRouter()
const auth = useAuthStore()

const usr = ref('')
const pwd = ref('')
const loading = ref(false)
const error = ref('')
const focusedField = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)

const STORAGE_KEY = 'tsf_remember'

onMounted(() => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const parsed = JSON.parse(saved)
      usr.value = parsed.u || ''
      pwd.value = parsed.p || ''
      rememberMe.value = true
    }
  } catch (e) {
    console.error('Failed to load saved login', e)
  }
})

async function handleLogin() {
  if (!usr.value || !pwd.value) {
    error.value = 'Please enter email and password.'
    return
  }
  loading.value = true
  error.value = ''

  try {
    if (rememberMe.value) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ u: usr.value, p: pwd.value }))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }

    const success = await auth.login(usr.value, pwd.value);

    if (success) {

      router.push('/dashboard')

    } else {
      
      error.value = 'Invalid credentials. Please try again.'


    }
  } catch (e) {
    error.value = 'Something went wrong. Please try again.'
  }

  loading.value = false
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@500&display=swap');
* { font-family: 'DM Sans', sans-serif; }

.page {
  min-height: 100vh;
  background: #0f2d12;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 1.5rem;
}

.bg-shapes { position: absolute; inset: 0; pointer-events: none; }
.shape { position: absolute; border-radius: 50%; }
.shape-1 { width: 350px; height: 350px; background: radial-gradient(circle, #2e7d3233, transparent 70%); top: -100px; right: -80px; }
.shape-2 { width: 250px; height: 250px; background: radial-gradient(circle, #81c78422, transparent 70%); bottom: -60px; left: -60px; }
.shape-3 { width: 180px; height: 180px; background: radial-gradient(circle, #1b5e2022, transparent 70%); top: 40%; left: 50%; transform: translateX(-50%); }

.content { position: relative; width: 100%; max-width: 380px; display: flex; flex-direction: column; align-items: center; gap: 1.75rem; }

.brand { text-align: center; }
.brand-icon { font-size: 3rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3)); }
.brand-name { font-size: 1.6rem; font-weight: 700; color: white; letter-spacing: -0.02em; }
.brand-sub { font-size: 0.82rem; color: rgba(255,255,255,0.45); margin-top: 0.25rem; }

.card {
  width: 100%;
  background: white;
  border-radius: 24px;
  padding: 1.75rem;
  box-shadow: 0 24px 60px rgba(0,0,0,0.4);
}
.card-title { font-size: 1.25rem; font-weight: 700; color: #1a1a1a; letter-spacing: -0.02em; }
.card-sub { font-size: 0.82rem; color: #aaa; margin-top: 0.2rem; margin-bottom: 1.5rem; }

.field-group { margin-bottom: 1rem; }
label { display: block; font-size: 0.72rem; font-weight: 700; color: #888; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem; }
.input-wrap { display: flex; align-items: center; gap: 0.5rem; border: 1.5px solid #e8e8e8; border-radius: 12px; padding: 0.7rem 0.9rem; background: #fafafa; transition: border 0.2s, background 0.2s, box-shadow 0.2s; }
.input-wrap.focused { border-color: #2e7d32; background: white; box-shadow: 0 0 0 3px rgba(46,125,50,0.1); }
.input-icon { font-size: 1rem; flex-shrink: 0; }
.input-wrap input { flex: 1; border: none; outline: none; background: transparent; font-size: 0.92rem; color: #1a1a1a; font-family: 'DM Sans', sans-serif; }
.input-wrap input::placeholder { color: #ccc; }
.toggle-pw { background: none; border: none; cursor: pointer; font-size: 1rem; padding: 0; line-height: 1; }

.remember-row { margin-bottom: 1rem; }
.remember-label { display: flex; align-items: center; gap: 0.5rem; font-size: 0.84rem; color: #666; cursor: pointer; font-weight: 500; width: fit-content; }
.remember-check { width: 16px; height: 16px; accent-color: #2e7d32; cursor: pointer; }

.error-msg { display: flex; align-items: center; gap: 0.5rem; background: #ffebee; color: #c62828; font-size: 0.82rem; padding: 0.7rem 0.9rem; border-radius: 10px; margin-bottom: 1rem; font-weight: 500; }

.login-btn {
  width: 100%;
  padding: 0.95rem;
  background: #1a4a1e;
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.15s;
  font-family: 'DM Sans', sans-serif;
}
.login-btn:hover { background: #2e7d32; }
.login-btn:active { transform: scale(0.98); }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-spinner { width: 18px; height: 18px; border: 2.5px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.footer { font-size: 0.72rem; color: rgba(255,255,255,0.25); text-align: center; }
</style>