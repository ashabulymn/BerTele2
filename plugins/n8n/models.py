from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.events.event import Event


class N8NWebhookPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    workflow_id: str | None = Field(default=None, alias="workflowId")
    execution_id: str | None = Field(default=None, alias="executionId")
    mode: str | None = None
    trigger: str | None = None
    event: str | None = None
    body: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_payload(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        normalized = dict(values)
        if "workflow_id" not in normalized and "workflowId" in normalized:
            normalized["workflow_id"] = normalized["workflowId"]
        if "execution_id" not in normalized and "executionId" in normalized:
            normalized["execution_id"] = normalized["executionId"]
        if "payload" not in normalized and "body" in normalized and isinstance(normalized["body"], dict):
            normalized["payload"] = normalized["body"]
        if "body" not in normalized and normalized.get("payload") is not None:
            normalized["body"] = normalized["payload"]
        if "metadata" not in normalized and "meta" in normalized and isinstance(normalized["meta"], dict):
            normalized["metadata"] = normalized["meta"]
        if "headers" not in normalized and "http" in normalized and isinstance(normalized["http"], dict):
            normalized["headers"] = normalized["http"].get("headers", {})
        return normalized


class N8NMessageRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    workflow_id: str | None = Field(default=None, alias="workflowId")
    node: str | None = None
    event_name: str | None = Field(default=None, alias="eventName")
    payload: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_request(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        normalized = dict(values)
        if "workflow_id" not in normalized and "workflowId" in normalized:
            normalized["workflow_id"] = normalized["workflowId"]
        if "event_name" not in normalized and "eventName" in normalized:
            normalized["event_name"] = normalized["eventName"]
        if "payload" not in normalized and "body" in normalized:
            normalized["payload"] = normalized["body"]
        return normalized

    @model_validator(mode="after")
    def validate_request(self) -> N8NMessageRequest:
        if not self.workflow_id and not self.node and not self.event_name:
            raise ValueError("N8N message request requires workflow_id, node, or event_name")
        return self


class N8NInboundEvent(Event):
    def __init__(
        self,
        *,
        workflow_id: str | None = None,
        execution_id: str | None = None,
        mode: str | None = None,
        trigger: str | None = None,
        event: str | None = None,
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        event_payload: dict[str, Any] = {
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "mode": mode,
            "trigger": trigger,
            "event": event,
            "metadata": metadata or {},
        }
        for key, value in (payload or {}).items():
            if key not in event_payload:
                event_payload[key] = value
        super().__init__(name="n8n.event.incoming", payload=event_payload)


class N8NOutboundEvent(Event):
    def __init__(
        self,
        *,
        workflow_id: str | None = None,
        node: str | None = None,
        event_name: str | None = None,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        event_payload: dict[str, Any] = {
            "workflow_id": workflow_id,
            "node": node,
            "event_name": event_name,
            "headers": headers or {},
            "metadata": metadata or {},
        }
        for key, value in (payload or {}).items():
            if key not in event_payload:
                event_payload[key] = value
        super().__init__(name="n8n.event.outgoing", payload=event_payload)
