from typing import List

from pydantic import Field, SecretStr, BaseModel, AnyHttpUrl
from pydantic_settings import SettingsConfigDict

from api.core.constants import ENV_PREFIX_CHALLENGE
from ._base import FrozenBaseConfig


class FrameworkImageConfig(BaseModel):
    name: str = Field(...)
    image: str = Field(...)


class VerificationConfig(FrozenBaseConfig):
    api_key: SecretStr = Field(..., min_length=12, max_length=128)
    endpoint: AnyHttpUrl = Field(...)
    startup_url: AnyHttpUrl = Field(...)
    extra: dict = Field(default_factory=dict)

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX_CHALLENGE}VERIFICATION_")


class ChallengeConfig(FrozenBaseConfig):
    api_key: SecretStr = Field(..., min_length=12, max_length=128)
    docker_ulimit: int = Field(...)
    verification: VerificationConfig = Field(...)
    bot_timeout: int = Field(..., ge=1)
    repeated_framework_count: int = Field(..., ge=1)
    framework_images: List[FrameworkImageConfig] = Field(...)

    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX_CHALLENGE, env_nested_delimiter="__"
    )


__all__ = [
    "FrameworkImageConfig",
    "ChallengeConfig",
    "VerificationConfig",
]
