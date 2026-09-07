from typing import Any, Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Envelope(Strict):
    schema_version: Literal["1.0"] = "1.0"
    scope_id: UUID
    source: Literal["EMAIL", "API", "FORM"]
    source_account_id: str = Field(min_length=1,max_length=100)
    source_id: str = Field(min_length=1,max_length=200)
    received_at: AwareDatetime
    sender: str = Field(default="",max_length=254)
    subject: str = Field(default="",max_length=500)
    content_text: str = Field(default="",max_length=50000)
    correlation_id: UUID
    payload: dict[str,Any] | None = None
    attachments: list[dict[str,Any]] = Field(default_factory=list,max_length=10)
    correction_context: dict[str,Any] | None = None
    ai_mode: Literal["fixture","live"] = "fixture"


class Stage(BaseModel):
    model_config = ConfigDict(extra="allow")
    schema_version: Literal["1.0"] = "1.0"
    scope_id: UUID
    correlation_id: UUID
    source_event_id: UUID
    job_id: UUID
    claim_token: UUID
    execution_id: str = Field(min_length=1,max_length=100)
    workflow_id: str = Field(min_length=1,max_length=100)
    incident_id: UUID | None = None
    revision: int | None = Field(default=None,ge=1)
    snapshot_id: UUID | None = None


class Claim(Strict):
    job_id: UUID | None = None
    owner: str = Field(min_length=1,max_length=200)
    limit: int = Field(default=10,ge=1,le=50)
    execution_id: str = "pending-execution-binding"
    workflow_id: str = "WF03"


class PlanContext(Strict):
    scope_id: UUID
    plan_id: UUID
    execution_id: str = Field(min_length=1,max_length=100)
    workflow_id: str = Field(min_length=1,max_length=100)
    resume_url: str | None = Field(default=None,max_length=2000)


class ActionCommand(Strict):
    scope_id: UUID
    action_id: UUID
    execution_id: str = Field(min_length=1,max_length=100)
    workflow_id: str = Field(min_length=1,max_length=100)
    claim_token: UUID | None = None


class Login(Strict):
    username: str = Field(min_length=1,max_length=100)
    password: str = Field(min_length=1,max_length=500)


class Decision(Strict):
    scope_id: UUID
    decision: Literal["APPROVE","REJECT","MODIFY"]
    expected_version: int = Field(ge=1)
    plan_hash: str = Field(min_length=64,max_length=64)
    comment: str = Field(min_length=1,max_length=2000)
    payload: dict[str,Any] | None = None


class Demo(Strict):
    scenario: Literal["supplier-delay","supplier-split","machine-breakdown","quality-issue","quality-shipped","unknown-input"]
    scope_id: UUID | None = None


class CustomEmail(Strict):
    subject: str = Field(min_length=1,max_length=500)
    content_text: str = Field(min_length=1,max_length=50000)


class ProviderResponseMetadata(Strict):
    request_id: str | None = Field(default=None,max_length=200)
    finish_reason: str | None = Field(default=None,max_length=100)
    prompt_tokens: int | None = Field(default=None,ge=0,le=10_000_000)
    completion_tokens: int | None = Field(default=None,ge=0,le=10_000_000)
    total_tokens: int | None = Field(default=None,ge=0,le=10_000_000)
    latency_ms: int | None = Field(default=None,ge=0,le=86_400_000)


class LiveExtractionInput(Strict):
    envelope: dict[str,Any]
    snapshot: dict[str,Any]
    candidate: dict[str,Any]
    model: str = Field(min_length=1,max_length=200)
    response_metadata: ProviderResponseMetadata = Field(default_factory=ProviderResponseMetadata)


class ImpactInput(Strict):
    snapshot: dict[str,Any]
    facts: dict[str,Any]


class RiskInput(Strict):
    impact: dict[str,Any]


class DraftInput(Strict):
    impact: dict[str,Any]
    risk: dict[str,Any]
    incident_id: str
    revision: int = Field(ge=1)


class ExtractInput(Strict):
    envelope: dict[str,Any]
    snapshot: dict[str,Any]
