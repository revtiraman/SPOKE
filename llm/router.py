"""Smart model router ? assigns the right model to each task.
Auto-detects API provider from token prefix and picks the best available model.
"""

from core.config import settings


def _provider() -> str:
    t = settings.hf_api_token
    if t.startswith("gsk_"):        return "groq"
    if t.startswith("sk-or-"):      return "openrouter"
    if t.startswith("together_"):   return "together"
    if t.startswith("csk-"):        return "cerebras"
    if t.startswith("hf_"):         return "huggingface"
    return "huggingface"


# ?? Model maps per provider ????????????????????????????????????????????????????
_MODELS = {
    "groq": {
        # Groq ? completely free, 6000 req/day, fastest inference
        "main":     "llama-3.3-70b-versatile",
        "planner":  "llama-3.3-70b-versatile",
        "coder":    "llama-3.3-70b-versatile",
        "fast":     "llama-3.3-70b-versatile",
        "tiny":     "llama3-8b-8192",
    },
    "together": {
        # Together.ai ? $25 free credit on signup
        "main":     "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "planner":  "deepseek-ai/DeepSeek-R1",
        "coder":    "Qwen/Qwen2.5-Coder-32B-Instruct",
        "fast":     "meta-llama/Llama-3.1-8B-Instruct-Turbo",
        "tiny":     "meta-llama/Llama-3.1-8B-Instruct-Turbo",
    },
    "openrouter": {
        # OpenRouter ? $5 free credit on signup
        "main":     "anthropic/claude-3-haiku",
        "planner":  "deepseek/deepseek-r1",
        "coder":    "qwen/qwen-2.5-coder-32b-instruct",
        "fast":     "meta-llama/llama-3.1-8b-instruct:free",
        "tiny":     "meta-llama/llama-3.1-8b-instruct:free",
    },
    "huggingface": {
        # HuggingFace ? free tier with monthly credits
        "main":     settings.main_brain_model,  # Kimi-K2
        "planner":  settings.planner_model,     # DeepSeek-R1
        "coder":    settings.coder_model,       # Qwen3-Coder-30B
        "fast":     settings.fast_model,        # Llama-3.3-70B
        "tiny":     settings.tiny_model,        # Qwen3-4B
    },
    "cerebras": {
        "main":     "llama-3.3-70b",
        "planner":  "llama-3.3-70b",
        "coder":    "llama-3.3-70b",
        "fast":     "llama3.1-8b",
        "tiny":     "llama3.1-8b",
    },
}


class ModelRouter:
    """Routes each pipeline stage to the best model for the detected provider."""

    def _m(self, role: str) -> str:
        provider = _provider()
        return _MODELS.get(provider, _MODELS["huggingface"]).get(role, settings.main_brain_model)

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
            "provider":   self.provider,
            "analyst":    self.analyst_model,
            "clarifier":  self.clarifier_model,
            "architect":  self.architect_model,
            "coder":      self.coder_model,
            "debugger":   self.debugger_model,
            "deployer":   self.deployer_model,
        }


router = ModelRouter()
