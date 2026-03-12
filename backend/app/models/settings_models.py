from typing import Literal

from pydantic import BaseModel

AiProvider = Literal["none", "ollama", "dnabot"]


class AiProviderResponse(BaseModel):
    active_provider: AiProvider


class SetAiProviderRequest(BaseModel):
    active_provider: AiProvider


class SetAiProviderResponse(BaseModel):
    status: Literal["updated"]
    active_provider: AiProvider
