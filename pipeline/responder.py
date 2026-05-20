import asyncio
import logging
import json
from groq import AsyncGroq
from core.config import (
    GROQ_API_KEY, GROQ_MODEL, CEREBRAS_API_KEY, GOOGLE_API_KEY, GOOGLE_MODEL,
    OPENROUTER_API_KEY, OPENROUTER_MODEL
)
from core.profile import get_profile

logger = logging.getLogger(__name__)

class Responder:
    def __init__(self, on_token, on_done, status_cb, usage_cb=None, provider_cb=None):
        from groq import AsyncGroq
        from core.config import GROQ_API_KEY
        # Disable auto-retries so DR fallback triggers instantly on 429
        self._client = AsyncGroq(api_key=GROQ_API_KEY, max_retries=0)
        self._on_token = on_token
        self._on_done = on_done
        self._status_cb = status_cb
        self._usage_cb = usage_cb
        self._provider_cb = provider_cb
        self._history = []
        self._total_tokens = 0

    def clear_history(self):
        self._history = []

    async def generate(self, question):
        asyncio.create_task(self._generate(question))

    async def _generate(self, question):
        self._status_cb("AI Thinking...")
        self._history.append({"role": "user", "content": question})
        system_prompt = get_profile().build_system_prompt()
        # Move critical rules to the END of history for maximum priority
        lang_reminder = ""
        from core.profile import get_profile
        p = get_profile()
        if p.language == "en":
            lang_reminder = "REMINDER: RESPOND IN SIMPLE ENGLISH ONLY. NO CONTRACTIONS. ONE SHORT PARAGRAPH (MAX 3 SENTENCES)."
        else:
            lang_reminder = "LEMBRETE: RESPONDA SEMPRE EM PORTUGUÊS BRASILEIRO. APENAS UM PARÁGRAFO CURTO (MÁX 3 FRASES)."

        messages = [{"role": "system", "content": system_prompt}] + self._history[-10:]
        messages.append({"role": "system", "content": lang_reminder})
        
        dr_chain = [
            ("GROQ", GROQ_MODEL),
            ("GROQ", "llama-3.1-8b-instant"),
            ("CEREBRAS", "llama3.1-8b"),
            ("OPENROUTER", OPENROUTER_MODEL),
            ("GEMINI", GOOGLE_MODEL)
        ]
        
        for provider, model_name in dr_chain:
            # Skip if API key is not configured/empty
            if provider == "GROQ" and not GROQ_API_KEY:
                continue
            if provider == "CEREBRAS" and not CEREBRAS_API_KEY:
                continue
            if provider == "OPENROUTER" and not OPENROUTER_API_KEY:
                continue
            if provider == "GEMINI" and not GOOGLE_API_KEY:
                continue

            try:
                msg = f"Trying {provider} ({model_name})..."
                logger.info(msg)
                self._status_cb(f"🤖 {msg}")
                
                if self._provider_cb:
                    self._provider_cb(provider, "🟡 Working...")
                
                if provider == "GROQ":
                    await self._generate_groq(model_name, messages)
                elif provider == "CEREBRAS":
                    await self._generate_cerebras(model_name, messages)
                elif provider == "OPENROUTER":
                    await self._generate_openrouter(model_name, messages)
                elif provider == "GEMINI":
                    await self._generate_gemini(model_name, messages)
                
                if self._provider_cb:
                    self._provider_cb(provider, "🟢 Online")
                
                self._on_done()
                self._status_cb("Ready")
                return 
            except Exception as e:
                logger.error(f"DR Fail: {provider}/{model_name} error: {type(e).__name__}: {e}")
                if self._provider_cb:
                    self._provider_cb(provider, "🔴 Error/Limit")
                continue 
        
        self._on_token("\n[SISTEMA]: Erro crítico. Todos os provedores falharam.")
        self._on_done()
        self._status_cb("Critical Error")

    async def _generate_groq(self, model, messages):
        # Ultra-short timeout for interview speed
        stream = await self._client.chat.completions.create(
            model=model, messages=messages, stream=True, timeout=2.0
        )
        full_response = []
        async for chunk in stream:
            if not chunk.choices: continue
            token = chunk.choices[0].delta.content
            if token:
                full_response.append(token)
                self._on_token(token)
        
        response_text = "".join(full_response).strip()
        if not response_text:
            raise ValueError("Groq returned empty content")
            
        self._history.append({"role": "assistant", "content": response_text})
        self._track_usage(len(response_text) // 4)

    async def _generate_cerebras(self, model, messages):
        from cerebras.cloud.sdk import AsyncCerebras
        from core.config import CEREBRAS_API_KEY
        c_client = AsyncCerebras(api_key=CEREBRAS_API_KEY, max_retries=0)
        response = await c_client.chat.completions.create(
            model=model, messages=messages, stream=False, timeout=2.0
        )
        content = response.choices[0].message.content
        if not content: raise ValueError("Cerebras returned empty")
        self._on_token(content)
        self._history.append({"role": "assistant", "content": content})
        self._track_usage(len(content) // 4)

    async def _generate_gemini(self, model, messages):
        from google import genai
        from core.config import GOOGLE_API_KEY
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        prompt = f"System: {messages[0]['content']}\n\n"
        for msg in messages[1:]:
            prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        # 2s timeout for Gemini
        response = await asyncio.wait_for(
            client.aio.models.generate_content(
                model=model,
                contents=prompt,
            ),
            timeout=2.0
        )
        content = response.text
        if not content: raise ValueError("Gemini returned empty")
        self._on_token(content)
        self._history.append({"role": "assistant", "content": content})
        self._track_usage(len(content) // 4)

    async def _generate_openrouter(self, model, messages):
        import aiohttp
        from core.config import OPENROUTER_API_KEY
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/humberto/interview-assistant",
            "X-Title": "Interview Copilot",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.5,
            "stream": True
        }
        
        timeout = aiohttp.ClientTimeout(connect=2.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers
            ) as resp:
                if resp.status != 200:
                    err_text = await resp.text()
                    raise RuntimeError(f"OpenRouter HTTP {resp.status}: {err_text}")
                
                full_response = []
                # Parse Server-Sent Events (SSE)
                async for line in resp.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            token = chunk["choices"][0]["delta"].get("content", "")
                            if token:
                                full_response.append(token)
                                self._on_token(token)
                        except Exception:
                            pass
                
                response_text = "".join(full_response).strip()
                if not response_text:
                    raise ValueError("OpenRouter returned empty content")
                
                self._history.append({"role": "assistant", "content": response_text})
                self._track_usage(len(response_text) // 4)

    def _track_usage(self, tokens):
        self._total_tokens += tokens
        if self._usage_cb:
            self._usage_cb(self._total_tokens)
