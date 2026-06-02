from app.core.config import settings

class AIService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.censorship_model_name = "beomi/beep-KcELECTRA-base-hate"
        
        # 우선순위 설정
        # 1. Groq (무료 + 초고속)
        if settings.GROQ_API_KEY:
            try:
                from groq import AsyncGroq
                self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
                self.gen_mode = "groq"
            except ImportError:
                self.gen_mode = None
                print("Warning: groq package is not installed.")
        # 2. OpenAI
        elif settings.OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                self.gen_mode = "openai"
            except ImportError:
                self.gen_mode = None
                print("Warning: openai package is not installed.")
        # 3. Gemini
        elif settings.GEMINI_API_KEY or settings.GEMINI_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY or settings.GEMINI_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.gen_mode = "gemini"
            except ImportError:
                self.gen_mode = None
                print("Warning: google-generativeai package is not installed.")
        else:
            self.gen_mode = None
            print("Warning: No AI API keys (Groq, OpenAI, Gemini) are set.")

        self.censorship_pipeline = None
        self._initialized = True

    def load_models(self):
        if self.censorship_pipeline is None:
            try:
                import torch
                from transformers import pipeline
            except ImportError:
                print("Warning: transformers or torch package is not installed.")
                return

            self.censorship_pipeline = pipeline(
                "text-classification", 
                model=self.censorship_model_name,
                device=0 if torch.cuda.is_available() else -1
            )

    async def get_ai_response(self, query: str) -> str:
        if not self.gen_mode:
            return "API 키가 설정되지 않았습니다."

        system_prompt = """
        너는 'TechBridge'의 AI 안내원이야.
        이 플랫폼은 IT 채용, 커뮤니티, 공모전, 기술 게시글을 한곳에서 탐색하는 IT 통합 플랫폼이야.
        친절하고 전문적인 말투로 답변해줘.
        한국어로 답변하고, 답변은 너무 길지 않게 3~4문장 내외로 해줘.
        """

        try:
            if self.gen_mode == "groq":
                response = await self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant", # 최신 지원 모델
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=500
                )
                return response.choices[0].message.content

            elif self.gen_mode == "openai":
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=500
                )
                return response.choices[0].message.content
            
            elif self.gen_mode == "gemini":
                prompt = f"{system_prompt}\n\n질문: {query}"
                response = await self.gemini_model.generate_content_async(prompt)
                return response.text
                
        except Exception as e:
            print(f"AI API Error ({self.gen_mode}): {e}")
            return "죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다."

    def check_censorship(self, text: str) -> dict:
        """비속어 및 공격적 표현 검열 (Hybrid 방식: 금칙어 + AI)"""
        
        # 1. 금칙어 리스트 (명백한 욕설)
        forbidden_words = [
            "시발", "씨발", "개새끼", "병신", "미친놈", "미친년", "존나", "지랄", "닥쳐", "뻐큐"
        ]
        
        # 공백을 제거한 텍스트로 체크하여 '시 발' 등도 차단
        clean_text = text.replace(" ", "").replace("\n", "").replace("\t", "")
        for word in forbidden_words:
            if word in clean_text:
                return {
                    'is_offensive': True,
                    'label': 'forbidden_word',
                    'score': 1.0
                }

        # 2. AI 모델 판단 (문맥적 공격성)
        if self.censorship_pipeline is None:
            self.load_models()
        if self.censorship_pipeline is None:
            return {'is_offensive': False, 'label': 'model_unavailable', 'score': 0.0}
        result = self.censorship_pipeline(text)[0]
        label = result['label']
        score = result['score']
        is_offensive = label in ['offensive', 'hate'] and score > 0.7
        return {'is_offensive': is_offensive, 'label': label, 'score': score}

ai_service = AIService()
