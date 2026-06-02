<template>
  <div class="about-container">

    <!-- ── 히어로 섹션 ── -->
    <section class="hero reveal" style="--index: 0">
      <div class="hero-badge">🚀 IT 개발자를 위한 공간</div>
      <h1 class="hero-title">개발자의 커리어,<br><span class="highlight">DevCareer</span>와 함께</h1>
      <p class="hero-desc">채용 공고부터 공모전, 커뮤니티, AI 질문 답변까지<br>개발자의 성장에 필요한 모든 것을 한 곳에서.</p>
      <div class="hero-buttons">
        <router-link to="/jobs" class="btn-primary">채용 공고 보기</router-link>
        <router-link to="/register" class="btn-secondary">무료로 시작하기</router-link>
      </div>
    </section>

    <!-- ── 주요 기능 소개 ── -->
    <section class="features-section">
      <div class="section-header reveal" style="--index: 1">
        <p class="subtitle">FEATURES</p>
        <h2 class="section-title">DevCareer가 제공하는 것들</h2>
        <p class="section-desc">개발자 커리어의 모든 단계를 함께합니다.</p>
      </div>

      <div class="features-grid">
        <div v-for="(feature, index) in features" :key="feature.id" class="feature-card card-hidden"
          :style="{ '--index': index + 2 }">
          <div class="feature-icon">{{ feature.icon }}</div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.desc }}</p>
        </div>
      </div>
    </section>

  </div>
</template>

<script>
export default {
  data() {
    return {
      features: [
        { id: 1, icon: '💼', title: '채용 공고', desc: '국내 주요 IT 기업의 최신 채용 공고를 한눈에 확인하세요. 기술 스택, 경력, 지역별 필터로 나에게 맞는 공고를 빠르게 찾을 수 있습니다.' },
        { id: 2, icon: '🏆', title: '공모전 정보', desc: '개발, 디자인, 아이디어 공모전 정보를 실시간으로 제공합니다. 마감일 알림 설정으로 놓치는 공모전 없이 도전해 보세요.' },
        { id: 3, icon: '💬', title: '커뮤니티', desc: '개발자들과 자유롭게 소통하세요. 취업 후기, 프로젝트 팀원 모집, 스터디 그룹까지 다양한 활동이 가능합니다.' },
        { id: 4, icon: '🤖', title: 'AI 질문 답변', desc: 'AI 어시스턴트가 코딩 질문, 이력서 첨삭, 면접 준비를 도와드립니다. 24시간 언제든지 질문해 보세요.' },
        { id: 5, icon: '🔔', title: '맞춤 알림', desc: '관심 기업, 기술 스택, 지역을 설정하면 새 공고가 올라올 때 바로 알림을 받을 수 있습니다.' },
        { id: 6, icon: '📝', title: '게시판', desc: '개발 관련 지식을 공유하고, 궁금한 점을 질문하세요. 활발한 활동으로 포인트와 배지를 획득할 수 있습니다.' },
      ]
    }
  },

  mounted() {
    this.$nextTick(() => this.initReveal())
  },

  methods: {
    initReveal() {
      if (this._observer) return

      this._observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible')
            this._observer.unobserve(entry.target)
          }
        })
      }, { threshold: 0.1 })

      const targets = document.querySelectorAll('.reveal, .card-hidden')
      if (targets.length === 0) {
        setTimeout(() => {
          this._observer = null
          this.initReveal()
        }, 200)
        return
      }
      targets.forEach(el => this._observer.observe(el))
    }
  }
}
</script>

<style scoped>
.about-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 40px 80px 40px;
}

/* ── 히어로 ── */
.hero {
  text-align: center;
  padding: 80px 0 60px;
}

.hero-badge {
  display: inline-block;
  background: rgba(93, 64, 55, 0.08);
  color: #5d4037;
  font-size: 14px;
  font-weight: 700;
  padding: 8px 20px;
  border-radius: 100px;
  margin-bottom: 28px;
  letter-spacing: 0.5px;
}

.hero-title {
  font-size: 48px;
  font-weight: 900;
  color: #1a1a1a;
  line-height: 1.25;
  margin-bottom: 20px;
  word-break: keep-all;
}

.highlight {
  background: linear-gradient(135deg, #5d4037, #a68b6a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  font-size: 17px;
  color: #000000;
  line-height: 1.8;
  margin-bottom: 40px;
  word-break: keep-all;
}

.hero-buttons {
  display: flex;
  gap: 14px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary {
  display: inline-block;
  background: linear-gradient(135deg, #5d4037, #a68b6a);
  color: white;
  font-size: 15px;
  font-weight: 700;
  padding: 14px 32px;
  border-radius: 100px;
  text-decoration: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.btn-primary:hover {
  opacity: 0.88;
  transform: translateY(-2px);
}

.btn-secondary {
  display: inline-block;
  background: white;
  color: #5d4037;
  font-size: 15px;
  font-weight: 700;
  padding: 14px 32px;
  border-radius: 100px;
  text-decoration: none;
  border: 1.5px solid rgba(93, 64, 55, 0.25);
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.btn-secondary:hover {
  border-color: #5d4037;
  transform: translateY(-2px);
}

/* ── 기능 소개 ── */
.features-section {
  padding-top: 20px;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.subtitle {
  color: #a68b6a;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 2px;
  margin-bottom: 12px;
}

.section-title {
  font-size: 30px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 10px;
}

.section-desc {
  font-size: 16px;
  color: #000000;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.feature-card {
  background: white;
  border-radius: 20px;
  padding: 32px 28px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
  border: 1.5px solid transparent;
  transition: box-shadow 0.3s ease, border-color 0.3s ease, transform 0.3s ease;
}

.feature-card:hover {
  box-shadow: 0 14px 40px rgba(93, 64, 55, 0.1);
  border-color: rgba(93, 64, 55, 0.15);
  transform: translateY(-4px);
}

.feature-icon {
  font-size: 36px;
  margin-bottom: 16px;
}

.feature-title {
  font-size: 17px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 10px;
}

.feature-desc {
  font-size: 14px;
  color: #000000;
  line-height: 1.7;
  word-break: keep-all;
}

/* ── 카드 등장 애니메이션 ── */
.reveal {
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.8s ease-out;
}

.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.card-hidden {
  opacity: 0;
  transform: translateY(20px);
  filter: blur(6px);
  transition: opacity 0.8s ease-out,
    filter 0.8s ease-out,
    transform 0.8s ease-out,
    box-shadow 0.3s ease,
    border-color 0.3s ease;
  transition-delay: calc(var(--index) * 0.07s);
}

.card-hidden.is-visible {
  opacity: 1;
  transform: translateY(0);
  filter: blur(0);
}

/* ── 반응형 ── */
@media (max-width: 768px) {
  .about-container {
    padding: 0 20px 60px 20px;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-desc {
    font-size: 15px;
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>