<template>
  <Transition name="fade">
    <div v-if="show" class="modal-overlay" @click.self="close">
      <div class="modal-card reveal-modal">
        <div class="modal-header">
          <div class="warning-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          </div>
          <h3>부적절한 표현 감지</h3>
        </div>
        
        <div class="modal-body">
          <p class="main-msg">작성하신 내용 중에 부적절한 표현이나 비속어가 포함되어 있는 것으로 판단되었습니다.</p>
          <div v-if="detail" class="detail-box">
            <span class="detail-label">상세 정보</span>
            <p class="detail-text">{{ detail }}</p>
          </div>
          <p class="sub-msg">커뮤니티 가이드라인을 준수하여 내용을 수정해 주세요.</p>
        </div>

        <div class="modal-footer">
          <button class="confirm-btn" @click="close">확인</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  show: Boolean,
  detail: String
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(43, 31, 18, 0.45);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-card {
  width: min(450px, 100%);
  background: #fffbf7;
  border-radius: 28px;
  box-shadow: 0 30px 60px -12px rgba(43, 31, 18, 0.25);
  overflow: hidden;
  border: 1px solid rgba(196, 142, 102, 0.2);
}

.modal-header {
  padding: 30px 30px 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.warning-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: #fff3e0;
  color: #ef6c00;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-header h3 {
  font-size: 1.4rem;
  font-weight: 800;
  color: #312821;
  letter-spacing: -0.02em;
}

.modal-body {
  padding: 0 30px 30px;
}

.main-msg {
  font-size: 1.05rem;
  font-weight: 600;
  color: #5d4a38;
  line-height: 1.6;
  margin-bottom: 20px;
  word-break: keep-all;
}

.detail-box {
  background: #fdf5eb;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  border: 1px solid rgba(196, 142, 102, 0.1);
}

.detail-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  color: #a68b6a;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}

.detail-text {
  font-size: 0.95rem;
  font-weight: 500;
  color: #835d43;
}

.sub-msg {
  font-size: 0.9rem;
  color: #a68b6a;
  line-height: 1.5;
}

.modal-footer {
  padding: 20px 30px 30px;
}

.confirm-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #312821, #835d43);
  color: #fff;
  border: none;
  border-radius: 16px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 10px 20px -10px rgba(131, 93, 67, 0.5);
}

.confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -10px rgba(131, 93, 67, 0.6);
}

.confirm-btn:active {
  transform: scale(0.98);
}

/* Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.reveal-modal {
  animation: modalIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>
