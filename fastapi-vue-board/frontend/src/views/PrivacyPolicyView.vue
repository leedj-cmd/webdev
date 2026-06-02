<template>
  <!-- 스킵 내비게이션: 키보드 사용자를 위한 본문 바로가기 -->
  <a href="#main-content" class="skip-link">본문 바로가기</a>

  <div class="privacy-container">
    <header class="privacy-header reveal" style="--index: 0" role="banner">
      <p class="subtitle" aria-label="섹션 분류: 법적 고지">LEGAL</p>
      <h1 class="title">🔒 개인정보처리방침</h1>
      <p class="header-desc"><b>DevCareer는 이용자의 개인정보를 소중히 여깁니다.</b></p>
      <p class="effective-date">
        <time datetime="2026-03-02">시행일: 2026년 3월 2일</time>
      </p>
    </header>

    <div class="policy-wrapper">
      <!-- aria-label로 목차 역할 명시 -->
      <nav class="toc-card card reveal" style="--index: 1" aria-label="개인정보처리방침 목차">
        <p class="toc-title" id="toc-heading">목차</p>
        <ul aria-labelledby="toc-heading">
          <li v-for="(section, i) in sections" :key="i">
            <a :href="`#section-${i}`">
              {{ i + 1 }}. {{ section.title }}
            </a>
          </li>
        </ul>
      </nav>

      <main id="main-content" class="sections">
        <!-- <section> 시맨틱 태그 + aria-labelledby로 제목 연결 -->
        <section v-for="(section, i) in sections" :key="i" :id="`section-${i}`" class="section-card card reveal"
          :style="`--index: ${i + 2}`" :aria-labelledby="`section-title-${i}`">
          <div class="section-header">
            <!-- 장식용 숫자는 스크린리더에서 제외 -->
            <span class="section-number" aria-hidden="true">0{{ i + 1 }}</span>
            <h2 class="section-title" :id="`section-title-${i}`">
              {{ section.title }}
            </h2>
          </div>

          <div class="section-body">
            <p v-for="(para, j) in section.paragraphs" :key="`para-${j}`" v-html="para"></p>

            <!-- 목록: aria-label로 맥락 제공 -->
            <ul v-if="section.items" :aria-label="`${section.title} 항목 목록`">
              <li v-for="(item, k) in section.items" :key="k">{{ item }}</li>
            </ul>

            <!-- 단락2가 있을 경우 -->
            <p v-if="section.paragraphs2" v-for="(para, j) in section.paragraphs2" :key="`para2-${j}`" v-html="para">
            </p>

            <!-- div 테이블 → 시맨틱 <table>로 교체 -->
            <table v-if="section.table" class="info-table" :aria-label="`${section.title} 표`">
              <caption class="sr-only">{{ section.title }} 관련 정보 표</caption>
              <thead>
                <tr>
                  <th v-for="col in section.table.headers" :key="col" scope="col">
                    {{ col }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, r) in section.table.rows" :key="r">
                  <!-- 첫 번째 셀은 행 헤더로 처리 -->
                  <th scope="row">{{ row[0] }}</th>
                  <td v-for="(cell, c) in row.slice(1)" :key="c">{{ cell }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>

    <!-- 문의 배너 -->
    <aside class="contact-banner card reveal" :style="`--index: ${sections.length + 3}`" aria-label="개인정보 문의 안내">
      <p class="banner-label">문의사항이 있으신가요?</p>
      <p class="contact-title">개인정보 관련 문의는 아래 이메일로 연락주세요</p>
      <a href="mailto:devcareer@example.com" class="contact-link" aria-label="개인정보 문의 이메일 보내기: devcareer@example.com">
        devcareer@example.com
      </a>
    </aside>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';

const sections = [
  {
    title: '수집하는 개인정보 항목',
    paragraphs: ['DevCareer는 회원가입 및 서비스 이용을 위해 아래의 최소한의 개인정보를 수집합니다.'],
    table: {
      headers: ['구분', '수집 항목', '수집 방법'],
      rows: [
        ['필수', '이메일 주소', '회원가입 시 직접 입력'],
        ['필수', '비밀번호 (암호화 저장)', '회원가입 시 직접 입력'],
        ['필수', '닉네임', '회원가입 시 직접 입력'],
      ],
    },
  },
  {
    title: '개인정보 수집 및 이용 목적',
    paragraphs: ['수집한 개인정보는 다음의 목적으로만 사용됩니다.'],
    items: [
      '회원 식별 및 로그인 서비스 제공',
      '커뮤니티 게시글 작성 및 댓글 서비스 제공',
      '공모전·채용공고 스크랩 기능 제공',
      '서비스 관련 공지 및 안내 발송',
      '부정 이용 방지 및 서비스 품질 향상',
    ],
  },
  {
    title: '개인정보 보유 및 이용 기간',
    paragraphs: [
      '회원 탈퇴 시 또는 수집·이용 목적이 달성된 후 지체 없이 해당 정보를 파기합니다.',
      '단, 관계 법령의 규정에 따라 보존할 필요가 있는 경우 일정 기간 보관할 수 있습니다.',
    ],
    items: [
      '소비자 보호에 관한 법률: 계약 또는 청약철회 기록 — 5년',
      '전자상거래 등에서의 소비자보호에 관한 법률: 불만 또는 분쟁처리 기록 — 3년',
      '통신비밀보호법: 서비스 이용 관련 로그 기록 — 3개월',
    ],
  },
  {
    title: '개인정보의 제3자 제공',
    paragraphs: [
      'DevCareer는 이용자의 개인정보를 원칙적으로 외부에 제공하지 않습니다.',
      '다만, 아래의 경우에는 예외로 합니다.',
    ],
    items: [
      '이용자가 사전에 동의한 경우',
      '법령의 규정에 의거하거나 수사 목적으로 법령에 정해진 절차와 방법에 따라 수사기관의 요구가 있는 경우',
    ],
  },
  {
    title: '개인정보 처리 위탁',
    paragraphs: [
      'DevCareer는 현재 개인정보 처리를 외부 업체에 위탁하지 않습니다.',
      '향후 위탁이 필요한 경우 이용자에게 사전 고지하고 동의를 받겠습니다.',
    ],
  },
  {
    title: '이용자의 권리와 행사 방법',
    paragraphs: ['이용자는 언제든지 아래의 권리를 행사할 수 있습니다.'],
    items: [
      '개인정보 열람 요청',
      '개인정보 수정·정정 요청',
      '개인정보 삭제(회원 탈퇴) 요청',
      '개인정보 처리 정지 요청',
    ],
    paragraphs2: ['권리 행사는 서비스 내 설정 메뉴 또는 이메일(devcareer@example.com)을 통해 가능합니다.'],
  },
  {
    title: '쿠키(Cookie) 사용 여부',
    paragraphs: [
      'DevCareer는 로그인 상태 유지 및 서비스 편의를 위해 로컬 스토리지(LocalStorage)를 활용하며, 별도의 추적 쿠키는 사용하지 않습니다.',
      '브라우저 설정에서 저장된 데이터를 언제든지 삭제할 수 있습니다.',
    ],
  },
  {
    title: '개인정보 보호책임자',
    paragraphs: [
      'DevCareer는 개인정보 처리에 관한 업무를 총괄하고, 이용자의 개인정보 관련 문의·불만·피해구제를 처리하기 위해 아래와 같이 개인정보 보호책임자를 지정하고 있습니다.',
    ],
    items: ['담당부서: DevCareer 개발팀', '이메일: devcareer@example.com'],
  },
  {
    title: '개인정보처리방침 변경',
    paragraphs: [
      '이 개인정보처리방침은 2025년 1월 1일부터 적용됩니다.',
      '내용이 변경될 경우 시행 7일 전부터 서비스 공지사항을 통해 안내합니다.',
      '본 방침은 학습 목적으로 운영되는 프로젝트에 적용되며, 실제 상업적 서비스와 무관합니다.',
    ],
  },
];

onMounted(() => {
  // prefers-reduced-motion: 애니메이션 비선호 사용자는 즉시 표시
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (prefersReduced) {
    document.querySelectorAll('.reveal').forEach((el) => {
      el.classList.add('is-visible');
    });
    return;
  }

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
/* ── 스킵 내비게이션 ── */
.skip-link {
  position: absolute;
  top: -100%;
  left: 16px;
  background: #5d4037;
  color: white;
  padding: 10px 18px;
  border-radius: 0 0 8px 8px;
  font-size: 14px;
  font-weight: 600;
  z-index: 9999;
  text-decoration: none;
  transition: top 0.2s;
}

.skip-link:focus {
  top: 0;
}

/* ── 스크린리더 전용 텍스트 ── */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* ── 전체 컨테이너 ── */
.privacy-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 60px 24px 100px;
  font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
  color: #000000;
}

/* ── 헤더 ── */
.privacy-header {
  margin-bottom: 48px;
}

.subtitle {
  color: #7a5c3a;
  /* #a68b6a → 대비비 개선 */
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

.header-desc {
  font-size: 16px;
  color: #000000;
  font-weight: 400;
  margin-bottom: 12px;
}

.effective-date {
  font-size: 13px;
  color: #000000;
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
  color: #7a5c3a;
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
  color: #000000;
  /* #888 → 대비비 4.5:1 이상 확보 */
  text-decoration: underline;
  /* 링크임을 색상 외 수단으로도 표시 */
  text-underline-offset: 2px;
  transition: color 0.2s;
  line-height: 1.5;
}

.toc-card ul li a:hover,
.toc-card ul li a:focus {
  color: #5d4037;
  font-weight: 600;
}

/* 포커스 스타일 명시 */
.toc-card ul li a:focus-visible {
  outline: 2px solid #5d4037;
  outline-offset: 3px;
  border-radius: 3px;
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

/* ── 시맨틱 테이블 ── */
.info-table {
  margin-top: 14px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #f0e8e0;
  border-collapse: collapse;
  width: 100%;
}

.info-table thead tr {
  background: #faf5f0;
}

.info-table th,
.info-table td {
  padding: 12px 16px;
  font-size: 13px;
  color: #000000;
  border-bottom: 1px solid #f5ede6;
  text-align: left;
}

.info-table th[scope='col'] {
  font-weight: 700;
  color: #5d4037;
  font-size: 12px;
}

.info-table th[scope='row'] {
  font-weight: 600;
  color: #5d4037;
}

.info-table tbody tr:last-child td,
.info-table tbody tr:last-child th {
  border-bottom: none;
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
  color: #7a5c3a;
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

.contact-link:focus-visible {
  outline: 3px solid #3e2723;
  outline-offset: 3px;
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

/* ── 애니메이션 비선호 사용자 대응 ── */
@media (prefers-reduced-motion: reduce) {
  .reveal {
    opacity: 1;
    transform: none;
    transition: none;
  }
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
</style>
