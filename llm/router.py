"""Smart model router — assigns the right model to each task."""

from core.config import settings


class ModelRouter:
    """Routes each pipeline stage to the optimal model based on budget and capability."""

    @property
    def transcription_model(self) -> str:
        return "openai/whisper-large-v3"

    @property
    def analyst_model(self) -> str:
        return settings.main_brain_model

    @property
    def clarifier_model(self) -> str:
        return settings.fast_model

    @property
    def architect_model(self) -> str:
        return settings.planner_model

    @property
    def coder_model(self) -> str:
        return settings.coder_model

    @property
    def debugger_model(self) -> str:
        return settings.coder_model

    @property
    def deployer_model(self) -> str:
        return settings.fast_model

    @property
    def utility_model(self) -> str:
        return settings.tiny_model

    def describe(self) -> dict[str, str]:
        return {
            "analyst": self.analyst_model,
            "clarifier": self.clarifier_model,
            "architect": self.architect_model,
            "coder": self.coder_model,
            "debugger": self.debugger_model,
            "deployer": self.deployer_model,
        }


router = ModelRouter()
