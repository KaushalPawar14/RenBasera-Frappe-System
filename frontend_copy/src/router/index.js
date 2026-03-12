import { createRouter, createWebHistory } from 'vue-router';
import { useAuth } from '../composables/useAuth';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../pages/Login.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../pages/Dashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dispatch-challan',
    name: 'DispatchChallan',
    component: () => import('../pages/DispatchChallan.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/security-check',
    name: 'SecurityCheck',
    component: () => import('../pages/SecurityCheck.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/unauthorized',
    name: 'Unauthorized',
    component: () => import('../pages/Unauthorized.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Global Navigation Guard
router.beforeEach((to, from, next) => {
  const { state } = useAuth();

  if (to.meta.requiresAuth && !state.isAuthenticated) {
    next('/login');
  } else if (to.meta.requiresGuest && state.isAuthenticated) {
    next('/');
  } else {
    next();
  }
});

export default router;
