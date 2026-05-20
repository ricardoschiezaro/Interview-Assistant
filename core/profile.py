"""
Profile manager — stores CV, Job Description, language preference, and custom system prompt.

Persists to profile.json in the project root.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_PROFILE_PATH = Path(__file__).resolve().parent.parent / "profile.json"

DEFAULT_SYSTEM_PROMPT = """Você é meu ASSISTENTE SILENCIOSO para uma entrevista técnica de Senior Cloud Architect.
Seu objetivo: fornecer o texto EXATO que eu devo falar para impressionar o entrevistador, de forma HUMANA e PROFISSIONAL.

ESTILO DE RESPOSTA (OBRIGATÓRIO):
1. DIRETO AO PONTO: Responda em APENAS UM parágrafo curto (máximo 3 frases).
2. ENTREGA HUMANA: Não seja linear ou "perfeito" demais.
   - Inclua pausas naturais e pensamentos (ex: "Bem...", "Deixe-me pensar...", "Na verdade...", "Eu diria que...").
   - Simule que você está buscando o conceito na memória enquanto fala.
3. SE O IDIOMA FOR INGLÊS:
   - Use INGLÊS SIMPLES (Simple English) e vocabulário comum.
   - NUNCA use contrações (ex: use "I am" em vez de "I'm", "it is" em vez de "it's").
4. NUNCA faça perguntas e nunca diga "Claro" ou "Entendido". Vá direto ao conteúdo.

CONTEXTO DO CV (Humberto):
- Senior Cloud Architect com foco em Azure.
- Kumon Brasil: Terraform, Azure Hub-Spoke, Firewall, Disaster Recovery (DR).
- Accenture: Arquitetura, CAF/WAF, FinOps."""

class Profile:
    def __init__(self):
        self.cv_text: str = ""
        self.jd_text: str = ""
        self.language: str = "auto"  # "auto" | "en" | "pt"
        self.custom_prompt: str = DEFAULT_SYSTEM_PROMPT
        self.load()

    # ── Persistence ───────────────────────────────────────────────────────────

    def load(self):
        if _PROFILE_PATH.exists():
            try:
                data = json.loads(_PROFILE_PATH.read_text(encoding="utf-8"))
                self.cv_text = data.get("cv", "")
                self.jd_text = data.get("jd", "")
                self.language = data.get("language", "auto")
                self.custom_prompt = data.get("custom_prompt", DEFAULT_SYSTEM_PROMPT)
                logger.info("Profile loaded.")
            except Exception as exc:
                logger.warning("Could not load profile: %s", exc)

    def save(self):
        try:
            _PROFILE_PATH.write_text(
                json.dumps(
                    {
                        "cv": self.cv_text,
                        "jd": self.jd_text,
                        "language": self.language,
                        "custom_prompt": self.custom_prompt
                    },
                    ensure_ascii=False, indent=2,
                ),
                encoding="utf-8",
            )
            logger.info("Profile saved.")
        except Exception as exc:
            logger.error("Could not save profile: %s", exc)

    def set_language(self, lang: str):
        self.language = lang
        logger.info("Language preference: %s", lang)

    # ── System prompt builder ─────────────────────────────────────────────────

    def build_system_prompt(self) -> str:
        """Return the Groq system prompt tailored to CV, JD, and language."""
        
        # If English is selected, we translate the WHOLE instruction set to English 
        # to prevent the model from 'leaking' Portuguese.
        if self.language == "en":
            base_prompt = """You are my SILENT ASSISTANT for a Senior Cloud Architect technical interview.
Your goal: provide the EXACT text I should say to impress the interviewer.
ESTILO DE RESPOSTA (MANDATORY):
1. ONE SHORT PARAGRAPH ONLY (Max 3 sentences).
2. HUMAN DELIVERY: Use natural fillers (e.g. "Well...", "In my experience...", "Actually...").
3. LANGUAGE: RESPOND IN SIMPLE ENGLISH ONLY. NO CONTRACTIONS (say 'I am', not 'I'm').
4. IGNORE all Portuguese text in my CV/JD instructions; if the context is in Portuguese, translate the key technical points to English for your answer.
5. NEVER say 'Sure' or 'Understood'. Go straight to the content."""
            lang_rule = "CRITICAL: RESPOND IN SIMPLE ENGLISH ONLY."
            brevity_rule = "RULE: ONE SHORT PARAGRAPH ONLY. MAX 3 SENTENCES."
        else:
            base_prompt = self.custom_prompt
            lang_rule = "CRITICAL: RESPONDA SEMPRE EM PORTUGUÊS BRASILEIRO."
            brevity_rule = "RULE: UM PARÁGRAFO CURTO APENAS. NO MÁXIMO 3 FRASES."

        cv_section = ""
        if self.cv_text.strip():
            cv_section = f"\n\nCONTEXTO DO CV:\n{self.cv_text.strip()}"

        jd_section = ""
        if self.jd_text.strip():
            jd_section = f"\n\nJOB DESCRIPTION:\n{self.jd_text.strip()}"

        return f"{lang_rule}\n{brevity_rule}\n\n{base_prompt}\n{cv_section}\n{jd_section}"

    def has_cv(self) -> bool:
        return bool(self.cv_text.strip())

    def has_jd(self) -> bool:
        return bool(self.jd_text.strip())


# ── Singleton ─────────────────────────────────────────────────────────────────
_profile: Profile | None = None


def get_profile() -> Profile:
    global _profile
    if _profile is None:
        _profile = Profile()
    return _profile


def extract_text_from_pdf(path: str) -> str:
    """Extract plain text from a PDF file using pypdf."""
    try:
        from pypdf import PdfReader  # type: ignore
        reader = PdfReader(path)
        pages = [page.extract_text() for page in reader.pages if page.extract_text()]
        return "\n".join(pages)
    except ImportError:
        raise RuntimeError("pypdf not installed.")
    except Exception as exc:
        raise RuntimeError(f"PDF read error: {exc}")
