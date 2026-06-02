<template>
  <div id="app">
    <div class="ambient ambient-one" />
    <div class="ambient ambient-two" />
    <div class="noise-layer" />
    <Navbar />
    <RouterView />
    <ChatWidget />
    <footer class="footer-wrapper">
    <div class="footer-inner">
      <div class="footer-content">
        <div class="footer-brand">
          <h2 class="footer-logo">Tech Bridge</h2>
          <p class="brand-desc">
            IT 개발자를 위한<br/>
            통합 커리어 플랫폼
          </p>
        </div>

        <div class="footer-links-group">
          <div class="link-column">
            <h3>서비스</h3>
            <ul>
              <li><a href="/posts">게시글</a></li>
              <li><a href="/jobs">채용 공고</a></li>
              <li><a href="/contests">공모전</a></li>
              <li><a href="/community">커뮤니티</a></li>
            </ul>
          </div>
          <div class="link-column">
            <h3>고객지원</h3>
            <ul>
              <li><a href="/notice">공지사항</a></li>
              <li><a href="/frequently">FAQ</a></li>
              <li><a href="/contact">문의하기</a></li>
              <li><a href="/partnership">제휴문의</a></li>
            </ul>
          </div>
          <div class="link-column">
            <h3>회사</h3>
            <ul>
              <li><a href="/about">사이트소개</a></li>
              <li><a href="/terms">이용약관</a></li>
              <li><a href="/privacy">개인정보처리방침</a></li>
            </ul>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <p>© 2026 TechBridge. All rights reserved.</p>
      </div>
    </div>
  </footer>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import Navbar from './components/Navbar.vue'
import ChatWidget from './components/ChatWidget.vue'
</script>

<style scoped>
#app {
  position: relative;
  min-height: 100vh;
  overflow: clip;
}

.ambient,
.noise-layer {
  pointer-events: none;
  position: fixed;
  inset: 0;
}

.ambient {
  z-index: -2;
  filter: blur(50px);
}

.ambient-one {
  top: -8rem;
  left: -10rem;
  width: 28rem;
  height: 28rem;
  background: radial-gradient(circle, rgba(198, 146, 109, 0.22), transparent 62%);
  animation: float 14s cubic-bezier(0.16, 1, 0.3, 1) infinite;
}

.ambient-two {
  inset: auto -8rem -10rem auto;
  width: 34rem;
  height: 34rem;
  background: radial-gradient(circle, rgba(143, 113, 86, 0.16), transparent 64%);
  animation: float 18s cubic-bezier(0.16, 1, 0.3, 1) infinite reverse;
}

.noise-layer {
  z-index: -1;
  opacity: 0.045;
  background-image:
    linear-gradient(rgba(58, 40, 24, 0.12) 1px, transparent 1px),
    linear-gradient(90deg, rgba(58, 40, 24, 0.12) 1px, transparent 1px);
  background-size: 140px 140px;
  mask-image: radial-gradient(circle at center, black, transparent 82%);
}
.footer-wrapper {
  background-color: #0b1324;
  color: #ffffff;
  padding: 100px 0 60px 0;
  font-family: 'Pretendard', sans-serif;
}

.footer-inner {
  /* 핵심: 너비를 최대(1400px 이상)로 키우거나 100%에 가깝게 설정 */
  max-width: 1400px; 
  margin: 0 auto;
  /* 좌우 패딩을 적당히 주어 화면 끝에 너무 붙지 않게 조절 */
  padding: 0 60px; 
}

.footer-content {
  display: flex;
  /* 양 끝으로 밀어버리는 설정 */
  justify-content: space-between; 
  align-items: flex-start;
  margin-bottom: 100px;
}

.footer-logo {
  font-size: 1.8rem;
  font-weight: 900;
  margin-bottom: 24px;
  letter-spacing: -0.03em;
}

.brand-desc {
  font-size: 0.95rem;
  color: #94a3b8;
  line-height: 1.8;
}

/* 오른쪽 링크 그룹 간격 */
.footer-links-group {
  display: flex;
  /* 각 카테고리 열 사이의 간격도 넉넉히 유지 */
  gap: 80px; 
}

.link-column h3 {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 28px;
  color: #ffffff;
}

.link-column ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.link-column ul li {
  margin-bottom: 14px;
}

.link-column ul li a {
  font-size: 0.9rem;
  color: #94a3b8;
  text-decoration: none;
  transition: color 0.2s;
}

.link-column ul li a:hover {
  color: #ffffff;
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 40px;
}

.footer-bottom p {
  font-size: 0.85rem;
  color: #4b5563;
}

/* 반응형 설정 */
@media (max-width: 1200px) {
  .footer-inner {
    padding: 0 40px;
  }
  .footer-links-group {
    gap: 50px;
  }
}
@keyframes float {
  0%,
  100% {
    transform: translate3d(0, 0, 0);
  }

  50% {
    transform: translate3d(0, -18px, 0);
  }
}
</style>
