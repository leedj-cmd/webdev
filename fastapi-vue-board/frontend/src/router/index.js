import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import JobListView from '../views/JobListView.vue'
import ContestListView from '../views/ContestListView.vue'
import PostView from '../views/PostView.vue'
import PostCreateView from '../views/PostCreateView.vue'
import CommunityView from '../views/CommunityView.vue'
import { useAuthStore } from '../stores/auth'
import TermsofServiceView from '@/views/TermsofServiceView.vue'
import NoticeView from '@/views/NoticeView.vue'
import PrivacyPolicyView from '@/views/PrivacyPolicyView.vue'
import ContactView from '@/views/ContactView.vue'
import PartnershipView from '@/views/PartnershipView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/jobs', name: 'jobs', component: JobListView },
    { path: '/contests', name: 'contests', component: ContestListView },
    { path: '/posts', name: 'posts', component: PostView },
    { path: '/posts/create', name: 'post-create', component: PostCreateView, meta: { requiresAuth: true } },
    { path: '/community', name: 'community', component: CommunityView },
    {
      path: '/community/create',
      name: 'community-create',
      component: () => import('../views/CommunityCreateView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/community/:id',
      name: 'community-detail',
      component: () => import('../views/CommunityDetailView.vue'),
    },
    { path: '/privacy', name: 'privacy', component: PrivacyPolicyView },
    { path: '/terms', name: 'terms', component: TermsofServiceView },
    { path: '/notice', name: 'notice', component: NoticeView },

    // 인증 관련
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/verify-email',
      name: 'verify-email',
      component: () => import('../views/VerifyEmailView.vue'),
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: () => import('../views/ResetPasswordView.vue'),
    },
    {
      path: '/admin/register',
      name: 'admin-register',
      component: () => import('../views/AdminRegisterView.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('../views/ChatView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/chat/:roomId',
      name: 'chat-room',
      component: () => import('../views/ChatView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/posts/:id',
      name: 'PostDetail',
      component: () => import('../views/PostDetailView.vue'),
    },
    {
      path: '/faq',
      name: 'faq',
      component: () => import('../views/AiChatView.vue'),
    },
    {
      path: '/frequently',
      component: () => import('../views/FrequentlyView.vue'),
    },
    { path: '/contact', name: 'contact', component: ContactView },
    { path: '/partnership', name: 'partnership', component: PartnershipView },
    { path: '/about', name: 'About', component: () => import('@/views/AboutView.vue') },

    // 관리자 전용
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/jobs/create',
      name: 'job-create',
      component: () => import('../views/JobFormView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/jobs/:id/edit',
      name: 'job-edit',
      component: () => import('../views/JobFormView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/contests/create',
      name: 'contest-create',
      component: () => import('../views/ContestFormView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/contests/:id/edit',
      name: 'contest-edit',
      component: () => import('../views/ContestFormView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/notice/:id',
      name: 'NoticeDetail',
      component: () => import('@/views/NoticeDetailView.vue')
    },

  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta.guestOnly && authStore.isLoggedIn) return { name: 'home' }
  if (to.meta.requiresAuth && !authStore.isLoggedIn) return { name: 'login' }
  if (to.meta.requiresAdmin && !authStore.isAdmin) return { name: 'home' }
})

export default router
