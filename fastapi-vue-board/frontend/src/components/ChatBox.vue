<template>
  <section class="chat-box" aria-label="AI 채팅">
    <div class="messages" ref="messageContainer">
      <div v-for="(message, index) in messages" :key="index" class="message-row" :class="message.type">
        <div class="message-bubble">
          {{ message.text }}
        </div>
      </div>
      <div v-if="isLoading" class="message-row bot">
        <div class="message-bubble typing">답변을 작성하는 중...</div>
      </div>
    </div>

    <form class="input-area" @submit.prevent="sendMessage">
      <textarea
        v-model="userInput"
        rows="1"
        placeholder="질문을 입력하세요..."
        :disabled="isLoading"
        @keydown.enter.prevent="sendMessage"
      ></textarea>
      <button type="submit" :disabled="isLoading || !userInput.trim()">전송</button>
    </form>
  </section>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import api from '@/api/axios'

defineProps({
  systemPrompt: {
    type: String,
    default: '',
  },
})

const userInput = ref('')
const isLoading = ref(false)
const messageContainer = ref(null)
const messages = ref([
  { type: 'bot', text: '안녕하세요. 커리어와 채용, 공모전 관련 질문을 도와드릴게요.' },
])

const scrollToBottom = async () => {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

watch(messages, scrollToBottom, { deep: true })

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const query = userInput.value.trim()
  messages.value.push({ type: 'user', text: query })
  userInput.value = ''
  isLoading.value = true

  try {
    const response = await api.post('/faq/ask', { query })
    messages.value.push({ type: 'bot', text: response.data.answer })
  } catch (error) {
    console.error('AI chat failed:', error)
    messages.value.push({
      type: 'bot',
      text: '답변을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.',
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.chat-box {
  display: flex;
  flex-direction: column;
  height: min(620px, calc(100vh - 220px));
  min-height: 420px;
  overflow: hidden;
  border: 1px solid #ece5de;
  border-radius: 20px;
  background: white;
}

.messages {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
  padding: 24px;
  background: #f8fafc;
}

.message-row {
  display: flex;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.bot {
  justify-content: flex-start;
}

.message-bubble {
  max-width: min(72%, 560px);
  padding: 12px 15px;
  border-radius: 16px;
  font-size: 0.95rem;
  line-height: 1.6;
  white-space: pre-wrap;
}

.message-row.user .message-bubble {
  border-bottom-right-radius: 4px;
  background: #835d43;
  color: white;
}

.message-row.bot .message-bubble {
  border: 1px solid #e2e8f0;
  border-bottom-left-radius: 4px;
  background: white;
  color: #312821;
}

.typing {
  color: #8b98aa;
}

.input-area {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #ece5de;
  background: white;
}

.input-area textarea {
  flex: 1;
  min-height: 44px;
  max-height: 120px;
  resize: vertical;
  padding: 12px 14px;
  border: 1px solid #ded6ce;
  border-radius: 12px;
  color: #312821;
  font: inherit;
  outline: none;
}

.input-area textarea:focus {
  border-color: #835d43;
}

.input-area button {
  min-width: 72px;
  border: 0;
  border-radius: 12px;
  background: #312821;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.input-area button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

@media (max-width: 640px) {
  .chat-box {
    height: calc(100vh - 180px);
    min-height: 360px;
  }

  .message-bubble {
    max-width: 86%;
  }
}
</style>
