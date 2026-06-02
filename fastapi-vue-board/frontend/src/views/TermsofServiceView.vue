<template>
  <div class="terms-container">

    <!-- 본문 바로가기 스킵 링크 -->
    <a href="#main-content" class="skip-link">본문 바로가기</a>

    <header class="terms-header reveal" style="--index: 0" role="banner">
      <p class="subtitle" aria-hidden="true">LEGAL</p>
      <h1 class="title">
        <span aria-hidden="true">📋</span> 이용약관
      </h1>
      <p class="terms-header-desc"><b>DevCareer 서비스 이용에 관한 약관입니다.</b></p>
      <p class="effective-date">
        <time datetime="2025-01-01">시행일: 2025년 1월 1일</time>
      </p>
    </header>

    <div class="policy-wrapper">

      <!-- 목차 네비게이션 -->
      <nav class="toc-card card reveal" style="--index: 1" aria-label="이용약관 목차">
        <p class="toc-title" id="toc-heading">목차</p>
        <ul aria-labelledby="toc-heading">
          <li v-for="(section, i) in sections" :key="i">
            <a :href="`#section-${i}`">{{ i + 1 }}. {{ section.title }}</a>
          </li>
        </ul>
      </nav>

      <!-- 메인 콘텐츠 -->
      <main id="main-content" class="sections" aria-label="이용약관 내용">
        <article v-for="(section, i) in sections" :key="i" :id="`section-${i}`" class="section-card card reveal"
          :style="`--index: ${i + 2}`" :aria-labelledby="`section-title-${i}`">
          <div class="section-header">
            <span class="section-number" aria-hidden="true">{{ String(i + 1).padStart(2, '0') }}</span>
            <h2 class="section-title" :id="`section-title-${i}`">{{ section.title }}</h2>
          </div>
          <div class="section-body">
            <p v-for="(para, j) in section.paragraphs" :key="`p-${j}`" v-html="para"></p>
            <ul v-if="section.items" :aria-label="`${section.title} 목록`">
              <li v-for="(item, k) in section.items" :key="k">{{ item }}</li>
            </ul>
          </div>
        </article>
      </main>

    </div>

    <!-- 문의 배너 -->
    <section class="contact-banner card reveal" :style="`--index: ${sections.length + 3}`" aria-label="문의 안내">
      <p class="banner-label" aria-hidden="true">문의사항이 있으신가요?</p>
      <h2 class="contact-title">이용약관 관련 문의는 아래 이메일로 연락주세요.</h2>
      <a href="mailto:devcareer@example.com" class="contact-link" aria-label="이용약관 문의 이메일 보내기: devcareer@example.com">
        devcareer@example.com
      </a>
    </section>

  </div>
</template>

<script setup>
import { onMounted } from 'vue';

const sections = [
  {
    title: '목적',
    paragraphs: [
      '이 약관은 DevCareer(이하 "서비스")가 제공하는 IT 취업 정보 및 커뮤니티 서비스의 이용과 관련하여 서비스와 이용자 간의 권리, 의무 및 책임사항을 규정함을 목적으로 합니다.',
      '본 서비스는 학습 및 비상업적 목적으로 운영되는 프로젝트이며, 실제 상업적 서비스와 무관합니다.',
    ]
  },
  {
    title: '용어의 정의',
    paragraphs: ['이 약관에서 사용하는 용어의 정의는 다음과 같습니다.'],
    items: [
      '"서비스"란 DevCareer가 제공하는 IT 채용 공고, 공모전 정보, 커뮤니티 등 모든 기능을 의미합니다.',
      '"이용자"란 이 약관에 따라 서비스에 접속하여 이용하는 회원 및 비회원을 의미합니다.',
      '"회원"이란 서비스에 회원가입을 완료하고 계정을 보유한 이용자를 의미합니다.',
      '"닉네임"이란 회원이 서비스 내에서 사용하는 식별 이름을 의미합니다.',
      '"게시물"이란 회원이 커뮤니티에 작성한 글, 댓글 등 일체의 정보를 의미합니다.',
    ]
  },
  {
    title: '약관의 효력 및 변경',
    paragraphs: [
      '이 약관은 서비스 화면에 게시하거나 기타 방법으로 공지함으로써 효력이 발생합니다.',
      '서비스는 필요한 경우 약관을 변경할 수 있으며, 변경된 약관은 시행 7일 전부터 공지합니다.',
      '이용자가 변경된 약관에 동의하지 않을 경우 서비스 이용을 중단하고 탈퇴할 수 있습니다.',
    ]
  },
  {
    title: '회원가입 및 계정 관리',
    paragraphs: ['이용자는 다음 사항에 동의하고 회원가입을 신청합니다.'],
    items: [
      '회원가입 시 이메일, 비밀번호, 닉네임을 정확하게 입력해야 합니다.',
      '타인의 정보를 도용하여 가입할 수 없습니다.',
      '계정 정보(이메일, 비밀번호)는 본인이 직접 관리해야 하며, 타인에게 양도 또는 공유할 수 없습니다.',
      '계정 도용 또는 부정 사용이 발견될 경우 즉시 서비스에 신고해야 합니다.',
      '서비스는 회원 1인당 1개의 계정만 허용합니다.',
    ]
  },
  {
    title: '서비스의 제공 및 변경',
    paragraphs: ['DevCareer는 다음과 같은 서비스를 제공합니다.'],
    items: [
      'IT 채용 공고 정보 제공',
      'IT 공모전 정보 제공',
      '개발자 커뮤니티 게시판 (자유게시판, 취업게시판, 공모전게시판 등)',
      '공고 및 공모전 스크랩 기능',
      '기타 서비스가 정하는 기능',
    ]
  },
  {
    title: '서비스 이용 제한',
    paragraphs: ['이용자는 다음 행위를 해서는 안 됩니다.'],
    items: [
      '타인의 개인정보를 무단으로 수집·이용하는 행위',
      '서비스의 운영을 방해하는 행위 (해킹, 서버 과부하 유발 등)',
      '허위 정보를 게시하거나 타인을 사칭하는 행위',
      '다른 이용자를 비방하거나 명예를 훼손하는 게시물 작성',
      '음란물, 불법 정보 등 관련 법령에 위반되는 내용 게시',
      '서비스의 지적 재산권을 침해하는 행위',
      '영리 목적의 무단 광고·홍보 게시',
    ]
  },
  {
    title: '게시물의 관리',
    paragraphs: [
      '회원이 작성한 게시물의 저작권은 해당 회원에게 있습니다.',
      '서비스는 이용자가 작성한 게시물이 이 약관 또는 관련 법령에 위반된다고 판단될 경우 사전 통지 없이 삭제하거나 이용을 제한할 수 있습니다.',
      '회원 탈퇴 시 작성한 게시물 및 댓글은 삭제되지 않으며, 닉네임은 "탈퇴한 사용자"로 변경됩니다.',
    ]
  },
  {
    title: '책임의 제한',
    paragraphs: [
      'DevCareer는 천재지변, 서버 장애 등 불가항력적 사유로 인한 서비스 제공 불능에 대해 책임을 지지 않습니다.',
      '서비스는 이용자 간 또는 이용자와 제3자 사이에서 발생한 분쟁에 대해 개입하지 않으며 이로 인한 손해를 배상할 책임이 없습니다.',
      '채용 공고 및 공모전 정보는 외부 데이터를 기반으로 하며, 정보의 정확성을 100% 보장하지 않습니다. 최종 확인은 원본 사이트에서 직접 확인하시기 바랍니다.',
    ]
  },
  {
    title: '회원 탈퇴',
    paragraphs: [
      '회원은 언제든지 서비스 내 설정 메뉴 또는 이메일을 통해 탈퇴를 요청할 수 있습니다.',
      '탈퇴 시 회원의 개인정보는 개인정보처리방침에 따라 처리됩니다.',
      '탈퇴 후에는 동일한 이메일로 재가입이 가능합니다.',
    ]
  },
  {
    title: '준거법 및 관할법원',
    paragraphs: [
      '이 약관은 대한민국 법률에 따라 해석되고 적용됩니다.',
      '서비스 이용과 관련하여 분쟁이 발생할 경우 민사소송법상의 관할법원을 제1심 법원으로 합니다.',
    ]
  },
];

onMounted(() => {
  const observerCallback = (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) entry.target.classList.add('is-visible');
    });
  };
  const observer = new IntersectionObserver(observerCallback, { threshold: 0.08 });
  document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
});
</script>

<style scoped>
/* ── 스킵 링크 ── */
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
  padding: 10px 20px;
  background: #5d4037;
  color: white;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  border-radius: 0 0 8px 0;
  z-index: 9999;
  transition: top 0.2s;
}

.skip-link:focus {
  top: 0;
}

.terms-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 60px 24px 100px;
  font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
  color: #2c2c2c;
}

/* ── 포커스 스타일 (키보드 접근성) ── */
*:focus-visible {
  outline: 2px solid #5d4037;
  outline-offset: 3px;
  border-radius: 4px;
}

/* ── 헤더 ── */
.terms-header {
  margin-bottom: 48px;
}

.subtitle {
  color: #a68b6a;
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.1em;
  margin-bottom: 10px;
}

.title {
  font-size: 36px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 10px;
}

.terms-header-desc {
  font-size: 16px;
  color: #000;
  font-weight: 400;
  margin-bottom: 12px;
}

.effective-date {
  font-size: 13px;
  color: #000;
}

/* ── 레이아웃 ── */
.policy-wrapper {
  display: flex;
  gap: 28px;
  align-items: flex-start;
}

/* ── 목차 ── */
.toc-card {
  width: 220px;
  flex-shrink: 0;
  padding: 28px 24px;
  position: sticky;
  top: 80px;
}

.toc-title {
  font-size: 16px;
  font-weight: 700;
  color: #a68b6a;
  letter-spacing: 0.08em;
  margin-bottom: 14px;
}

.toc-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.toc-card ul li a {
  font-size: 13px;
  color: #000;
  text-decoration: none;
  transition: color 0.2s;
  line-height: 1.5;
}

.toc-card ul li a:hover {
  color: #5d4037;
  font-weight: 600;
}

/* ── 섹션 영역 ── */
.sections {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  padding: 36px 40px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.section-number {
  font-size: 28px;
  font-weight: 900;
  color: #e8ddd5;
  line-height: 1;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #3e2723;
}

.section-body p {
  font-size: 14px;
  color: #000000;
  line-height: 1.8;
  margin-bottom: 10px;
}

.section-body ul {
  padding-left: 18px;
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-body ul li {
  font-size: 14px;
  color: #000000;
  line-height: 1.7;
}

/* ── 문의 배너 ── */
.contact-banner {
  margin-top: 40px;
  padding: 40px 48px;
  text-align: center;
  background: linear-gradient(135deg, #fdfaf7 0%, #f5ede6 100%);
}

.banner-label {
  font-size: 12px;
  font-weight: 700;
  color: #a68b6a;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}

.contact-title {
  font-size: 18px;
  font-weight: 700;
  color: #3e2723;
  margin-bottom: 16px;
}

.contact-link {
  display: inline-block;
  padding: 12px 28px;
  background: #5d4037;
  color: white;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
  transition: background 0.2s;
}

.contact-link:hover {
  background: #3e2723;
}

/* ── 공통 카드 ── */
.card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.04);
}

/* ── 애니메이션 ── */
.reveal {
  opacity: 0;
  transform: translateY(1.5rem);
  transition: all 0.7s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: calc(var(--index, 0) * 0.07s);
}

.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* ── 반응형 ── */
@media (max-width: 720px) {
  .policy-wrapper {
    flex-direction: column;
  }

  .toc-card {
    width: 100%;
    position: static;
  }

  .section-card {
    padding: 28px 24px;
  }

  .contact-banner {
    padding: 32px 24px;
  }
}

/* ── 고대비 모드 지원 ── */
@media (prefers-contrast: high) {

  .section-body p,
  .section-body ul li,
  .toc-card ul li a {
    color: #000;
  }

  .contact-link {
    border: 2px solid #000;
  }
}

/* ── 애니메이션 줄이기 설정 지원 ── */
@media (prefers-reduced-motion: reduce) {
  .reveal {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
</style>