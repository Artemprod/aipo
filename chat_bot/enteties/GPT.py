from dataclasses import dataclass
from datetime import datetime


@dataclass
class OpenAI_KEY:
    key: str


@dataclass
class OpenAIGPT:

    id: int
    token: OpenAI_KEY
    last_request: datetime | None

    @dataclass
    class RequestParameters:
        model: str
        timeout: int
        messages: list
        n: int | None
        stop: int | None
        temperature: int | None
        frequency_penalty: int | None
        top_p: int | None
        presence_penalty: int | None

    request_parameters: RequestParameters | None


@dataclass
class Prompt:
    system_prompt:str
