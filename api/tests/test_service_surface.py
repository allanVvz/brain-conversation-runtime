from __future__ import annotations

import base64
import json
import os

import pytest

os.environ.setdefault("SUPABASE_OFFLINE", "true")
os.environ.setdefault("KNOWLEDGE_TAXONOMY_OFFLINE", "true")
os.environ.setdefault("CURRENT_SCHEMA_VERSION", "130")

import main
from repositories import runtime as runtime_repository
from services import supabase_client
from middleware.auth import is_public_path
from workers.runner import WORKERS


FORBIDDEN_PREFIXES = (
    "/auth",
    "/personas",
    "/knowledge",
    "/webhooks",
    "/messages",
    "/messaging",
)


def test_service_identity_and_readiness_surface():
    assert main.app.title == "Brain Conversation Runtime"
    paths = set(main.app.openapi()["paths"])
    assert "/health" in paths
    assert "/health/ready" in paths
    assert "/process" in paths
    assert "/internal/v1/conversations/context" in paths
    assert "/internal/v1/conversations/execute" in paths
    assert "/internal/v1/agents/leads/{lead_ref}/journey-events" in paths
    assert "/internal/v1/agents/leads/{lead_ref}/journey-state" in paths
    assert "/internal/v1/runtime/leads/{lead_ref}/pause" in paths
    assert "/internal/v1/runtime/leads/{lead_ref}/resume" in paths
    assert "/internal/conversations/context" not in paths


def test_worker_group_is_domain_scoped():
    assert set(WORKERS) == {
        "health_check",
        "inactivity_recovery",
        "wa_validator",
    }


def test_public_surface_excludes_other_domains():
    paths = set(main.app.openapi()["paths"])
    offenders = sorted(
        path
        for path in paths
        for prefix in FORBIDDEN_PREFIXES
        if path == prefix or path.startswith(prefix + "/")
    )
    assert offenders == []


def test_only_versioned_internal_journey_paths_are_service_authenticated():
    assert is_public_path("/internal/v1/agents/leads/42/journey-events") is True
    assert is_public_path("/internal/v1/agents/leads/42/journey-state") is True
    assert is_public_path("/internal/agents/leads/42/journey-events") is False
    assert is_public_path("/internal/v1/runtime/leads/42/resume") is True
    assert is_public_path("/internal/runtime/leads/42/resume") is False


def _jwt_for_role(role: str) -> str:
    payload = base64.urlsafe_b64encode(
        json.dumps({"role": role}).encode()
    ).decode().rstrip("=")
    return f"header.{payload}.signature"


def test_database_jwt_is_restricted_to_manifest_role(monkeypatch):
    expected = _jwt_for_role("brain_runtime")
    monkeypatch.setenv("BRAIN_DB_JWT", expected)
    assert supabase_client._validated_db_jwt() == expected

    monkeypatch.setenv("BRAIN_DB_JWT", _jwt_for_role("service_role"))
    with pytest.raises(RuntimeError, match="brain_runtime"):
        supabase_client._validated_db_jwt()


def test_readiness_uses_image_schema_requirement_and_build_metadata(monkeypatch):
    from routes import health

    monkeypatch.setenv("CURRENT_SCHEMA_VERSION", "131")
    monkeypatch.setenv("REQUIRED_SCHEMA_VERSION", "131")
    monkeypatch.setenv("SOURCE_SHA", "a" * 40)
    monkeypatch.setenv("BUILD_DIGEST", "sha256:image")
    monkeypatch.setattr(health.supabase_client, "ping_supabase", lambda: (True, "ok"))

    result = health.health_ready()

    assert result["status"] == "ready"
    assert result["required_schema_version"] == 131
    assert result["source_sha"] == "a" * 40
    assert result["build_digest"] == "sha256:image"


def test_legacy_database_module_is_runtime_repository_alias():
    assert supabase_client is runtime_repository
