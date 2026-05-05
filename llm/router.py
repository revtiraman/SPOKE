"""Smart model router ? assigns the right model to each task.
Auto-detects API provider from token prefix and picks the best available model.

Supported providers (set HF_API_TOKEN to the key):
  hf_...        HuggingFace Inference API
  gsk_...       Groq (free, fast)
  csk_...       Cerebras (free tier, very fast)
  AIza...       Google Gemini (free tier, excellent coder)
  together_...  Together.ai ($25 free credit)
  sk-or-...     OpenRouter
"""

from core.config import settings


def _provider() -> str:
    t = settings.hf_api_token
    if t.startswith("gsk_"):        return "groq"
    if t.startswith("csk-"):        return "cerebras"
    if t.startswith("AIza"):        return "gemini"
    if t.startswith("together_"):   return "together"
    if t.startswith("sk-or-"):      return "openrouter"
    if t.startswith("hf_"):         return "huggingface"
    return "huggingface"


# Confirmed working models per provider
_MODELS = {
    "groq": {
        # Free, 6000 req/day, fast ? groq.com
        "main":    "llama-3.3-70b-versatile",
        "planner": "llama-3.3-70b-versatile",
        "coder":   "llama-3.3-70b-versatile",
        "fast":    "llama-3.3-70b-versatile",
        "tiny":    "llama3-8b-8192",
    },
    "cerebras": {
        # Free tier ? cerebras.ai ? confirmed working from logs
        "main":    "llama3.1-8b",
        "planner": "llama3.1-8b",
        "coder":   "llama3.1-8b",   # FIXED: was qwen-3-235b which doesn't exist
        "fast":    "llama3.1-8b",
        "tiny":    "llama3.1-8b",
    },
    "gemini": {
        # Google Gemini free tier ? aistudio.google.com
        # gemini-2.0-flash is excellent for code generation
        "main":    "gemini-2.0-flash",
        "planner": "gemini-2.0-flash",
        "coder":   "gemini-2.0-flash",  # Best free coder available
        "fast":    "gemini-2.0-flash",
        "tiny":    "gemini-2.0-flash",
    },
    "together": {
        # $25 free credit ? together.ai
        "main":    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "planner": "deepseek-ai/DeepSeek-R1",
        "coder":   "Qwen/Qwen2.5-Coder-32B-Instruct",
        "fast":    "meta-llama/Llama-3.1-8B-Instruct-Turbo",
        "tiny":    "meta-llama/Llama-3.1-8B-Instruct-Turbo",
    },
    "openrouter": {
        "main":    "anthropic/claude-3-haiku",
        "planner": "deepseek/deepseek-r1",
        "coder":   "qwen/qwen-2.5-coder-32b-instruct",
        "fast":    "meta-llama/llama-3.1-8b-instruct:free",
        "tiny":    "meta-llama/llama-3.1-8b-instruct:free",
    },
    "huggingface": {
        "main":    settings.main_brain_model,
        "planner": settings.planner_model,
        "coder":   settings.coder_model,
        "fast":    settings.fast_model,
        "tiny":    settings.tiny_model,
    },
}


class ModelRouter:
    def _m(self, role: str) -> str:
        p = _provider()
        return _MODELS.get(p, _MODELS["huggingface"]).get(role, "llama3.1-8b")

    @property
    def provider(self) -> str:
        return _provider()

    @property
    def transcription_model(self) -> str:
        return "openai/whisper-large-v3"

    @property
    def analyst_model(self) -> str:
        return self._m("main")

    @property
    def clarifier_model(self) -> str:
        return self._m("fast")

    @property
    def planner_model(self) -> str:
        return self._m("planner")

    @property
    def architect_model(self) -> str:
        return self._m("planner")

    @property
    def coder_model(self) -> str:
        return self._m("coder")

    @property
    def debugger_model(self) -> str:
        return self._m("coder")

    @property
    def deployer_model(self) -> str:
        return self._m("fast")

    @property
    def utility_model(self) -> str:
        return self._m("tiny")

    def describe(self) -> dict[str, str]:
        return {
            "provider":  self.provider,
            "analyst":   self.analyst_model,
            "clarifier": self.clarifier_model,
            "architect": self.architect_model,
            "coder":     self.coder_model,
            "debugger":  self.debugger_model,
            "deployer":  self.deployer_model,
        }


router = ModelRouter()
