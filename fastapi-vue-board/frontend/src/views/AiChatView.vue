<template>
  <div class="ai-chat-page">
    <header class="chat-header">
      <h1>🤖 AI 커리어 어시스턴트</h1>
      <p>취업, 공모전, 커리어에 대해 무엇이든 물어보세요!</p>
    </header>
    
    <div class="chat-wrapper">
      <ChatBox systemPrompt="당신은 IT 커리어 전문가입니다. 채용 공고와 공모전 정보를 바탕으로 조언해주세요." />
    </div>
  </div>
</template>

<script setup>
import ChatBox from '../components/ChatBox.vue'
</script>

<style scoped>
.ai-chat-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}
.chat-header {
  text-align: center;
  margin-bottom: 30px;
}
.chat-wrapper {
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}
</style>