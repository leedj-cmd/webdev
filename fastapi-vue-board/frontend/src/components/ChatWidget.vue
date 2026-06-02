<template>
  <div class="chat-widget-container">
    <!-- Floating Button -->
    <button class="chat-toggle-btn" @click="toggleChat" :class="{ 'active': isOpen }">
      <span v-if="!isOpen">💬</span>
      <span v-else>✖</span>
    </button>

    <!-- Chat Window -->
    <div v-if="isOpen" class="chat-window">
      <div class="chat-header">
        <h3>AI FAQ 챗봇</h3>
        <p>무엇이든 물어보세요!</p>
      </div>
      
      <div class="chat-messages" ref="messageContainer">
        <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.type]">
          <div class="message-content">
            {{ msg.text }}
          </div>
        </div>
        <div v-if="isLoading" class="message bot">
          <div class="message-content typing">
            입력 중...
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <input 
          v-model="userInput" 
          @keyup.enter="sendMessage" 
          placeholder="질문을 입력하세요..." 
          :disabled="isLoading"
        />
        <button @click="sendMessage" :disabled="isLoading || !userInput.trim()">
          전송
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import axios from '@/api/axios'

const isOpen = ref(false)
const userInput = ref('')
const isLoading = ref(false)
const messageContainer = ref(null)

const messages = ref([
  { type: 'bot', text: '안녕하세요! MJC 커리어 플랫폼 AI 도우미입니다. 무엇을 도와드릴까요?' }
])

const toggleChat = () => {
  isOpen.value = !isOpen.value
}

const scrollToBottom = async () => {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

watch(messages, () => {
  scrollToBottom()
}, { deep: true })

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const userText = userInput.value
  messages.value.push({ type: 'user', text: userText })
  userInput.value = ''
  isLoading.value = true

  try {
    const response = await axios.post('/faq/ask', { query: userText })
    messages.value.push({ 
      type: 'bot', 
      text: response.data.answer 
    })
  } catch (error) {
    console.error('FAQ Error:', error)
    messages.value.push({ 
      type: 'bot', 
      text: '죄송합니다. 관련 답변을 찾지 못했습니다. 다른 질문을 입력해 주시겠어요?' 
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.chat-widget-container {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 9999;
  font-family: 'Pretendard', sans-serif;
}

.chat-toggle-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #c6926d, #8f7156);
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.chat-toggle-btn:hover {
  transform: scale(1.1);
}

.chat-toggle-btn.active {
  background: #333;
}

.chat-window {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 360px;
  height: 540px;
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 12px 48px rgba(100, 70, 40, 0.16);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid #f0ede9;
}

@keyframes slideUp {
  from { transform: translateY(30px) scale(0.95); opacity: 0; }
  to { transform: translateY(0) scale(1); opacity: 1; }
}

.chat-header {
  padding: 24px 20px;
  background: linear-gradient(135deg, #5d4037 0%, #4a342c 100%);
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-header h3 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.chat-header p {
  margin: 6px 0 0;
  font-size: 0.85rem;
  opacity: 0.85;
  font-weight: 500;
}

.chat-messages {
  flex: 1;
  padding: 24px 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #fdfaf7;
  scrollbar-width: thin;
  scrollbar-color: #e8ddd4 transparent;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background-color: #e8ddd4;
  border-radius: 10px;
}

.message {
  max-width: 85%;
}

.message-content {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 0.92rem;
  line-height: 1.6;
  font-weight: 500;
}

.message.user {
  align-self: flex-end;
}

.message.user .message-content {
  background: #8b6f5a;
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 12px rgba(139, 111, 90, 0.2);
}

.message.bot {
  align-self: flex-start;
}

.message.bot .message-content {
  background: #ffffff;
  color: #3e2723;
  border: 1.5px solid #ede5dc;
  border-bottom-left-radius: 4px;
  box-shadow: 0 4px 12px rgba(100, 70, 40, 0.05);
}

.typing {
  font-style: italic;
  color: #a68b6a;
}

.chat-input-area {
  padding: 20px;
  display: flex;
  gap: 12px;
  border-top: 1px solid #f0ede9;
  background: white;
}

.chat-input-area input {
  flex: 1;
  padding: 12px 16px;
  border: 1.5px solid #e8ddd4;
  border-radius: 14px;
  outline: none;
  font-size: 0.95rem;
  transition: all 0.2s;
  background: #faf8f6;
}

.chat-input-area input:focus {
  border-color: #a68b6a;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(166, 139, 106, 0.1);
}

.chat-input-area button {
  padding: 0 20px;
  background: #5d4037;
  color: white;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.chat-input-area button:hover:not(:disabled) {
  background: #3e2723;
  transform: translateY(-1px);
}

.chat-input-area button:disabled {
  background: #d6c4b0;
  cursor: not-allowed;
}
</style>
