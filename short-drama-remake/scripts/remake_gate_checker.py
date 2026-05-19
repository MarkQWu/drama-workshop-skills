#!/usr/bin/env python3
"""Deterministic checker skeleton for short-drama-remake gates.

The first implementation validates fixture contracts and critical invariants.
It intentionally does not judge creative quality; that belongs to LLM review.
Fixture files are JSON-compatible YAML so this script can run with stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_FIXTURE_FIELDS = {
    "fixture_id",
    "title",
    "problem_refs",
    "category",
    "initial_project_state",
    "user_input",
    "expected_route",
    "expected_result",
    "node_invocation_trace",
    "assertions",
}

FORBIDDEN_P10_FULL_NODE_CALLS = {
    "resume.restore",
    "source.validate",
    "reference_map.validate",
    "fact_gate.validate",
}

DEFAULT_FORBIDDEN_SCRIPT_READS = {
    "short-drama/SKILL.md",
    "short-drama/references/opening-rules.md",
    "short-drama/references/ai-live-rules.md",
    "research-notes.md",
    "00_source/bundles/eps_011-020.md",
    "00_source/episodes/ep_012.md",
}

DEFAULT_FORBIDDEN_READ_PREFIXES = (
    "short-drama/references/",
)

REQUIRED_MARKET_ADAPTATION_REPORT_FIELDS = {
    "source_market",
    "target_market",
    "layer_classification",
    "reference_function_map",
    "source_market_mechanism_map",
    "target_market_replacement_map",
    "must_not_carry_over",
    "overseas_genre_promise",
    "paywall_pressure",
    "distance_check",
    "blockers",
    "warnings",
}

POSTFLIGHT_REPORT_STATUSES = {
    "passed",
    "blocked",
    "needs_revision",
    "needs_user_review",
    "pending_commit",
    "pending_state_update",
    "locked",
    "stale",
}

POSTFLIGHT_REGISTRY_OWNED_FIELDS = {
    "gate_status",
    "current_pointer",
    "last_transaction_id",
}

CONTROL_LAYERS = {"foundation", "skeleton", "flesh"}

MARKET_ADAPTATION_REQUIRED_NODES = {
    "project_plan.prepare",
    "script_draft.preflight",
}


class CheckFailure(Exception):
    pass


def assert_schema_yaml_syntax(path: Path) -> None:
    """Lightweight YAML subset lint for repo schema contracts."""

    previous_same_indent: dict[int, tuple[int, str]] = {}
    block_scalar_parent_indent: int | None = None
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if "\t" in raw_line:
            raise CheckFailure(f"{path}:{line_no}: tabs are not allowed in schema YAML")
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped == "---":
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent % 2 != 0:
            raise CheckFailure(f"{path}:{line_no}: indentation must use multiples of two spaces")

        content = raw_line[indent:]
        if block_scalar_parent_indent is not None:
            if indent > block_scalar_parent_indent:
                continue
            block_scalar_parent_indent = None

        for previous_indent in list(previous_same_indent):
            if previous_indent > indent:
                del previous_same_indent[previous_indent]

        if content.startswith("- "):
            previous_same_indent[indent] = (line_no, content)
            continue

        flow_list_match = re.search(r":\s*\[(.*)\]\s*$", content)
        if flow_list_match:
            for item in flow_list_match.group(1).split(","):
                value = item.strip()
                if ":" in value and not (value.startswith('"') or value.startswith("'")):
                    raise CheckFailure(
                        f"{path}:{line_no}: flow list item with ':' must be quoted for strict YAML parsing"
                    )

        previous = previous_same_indent.get(indent)
        if previous and previous[1].startswith("- "):
            raise CheckFailure(
                f"{path}:{line_no}: mapping item follows list item at the same indent; "
                f"add '- ' or outdent it. Previous list item at line {previous[0]}."
            )

        if not re.match(r"^[A-Za-z0-9_.-][^:]*:\s*(.*)$", content):
            raise CheckFailure(f"{path}:{line_no}: expected a mapping key or '- ' list item")
        if re.match(r"^[A-Za-z0-9_.-][^:]*:\s*[>|-]\s*$", content):
            block_scalar_parent_indent = indent
        previous_same_indent[indent] = (line_no, content)


def load_json_compatible_yaml(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CheckFailure(
            f"{path} is not JSON-compatible YAML. Keep fixture files parseable by stdlib json for now: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise CheckFailure(f"{path} must contain a mapping/object at top level")
    return data


def assert_required_fields(fixture: dict[str, Any], path: Path) -> None:
    missing = sorted(REQUIRED_FIXTURE_FIELDS - fixture.keys())
    if missing:
        raise CheckFailure(f"{path} missing required fields: {', '.join(missing)}")


def assert_required_fixture_files(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    fixture_dir = path.parent
    required_dirs = [
        fixture_dir / "project",
        fixture_dir / "snapshots" / "before",
        fixture_dir / "snapshots" / "after_expected",
    ]
    required_files = [
        fixture_dir / "call_trace.expected.yaml",
        fixture_dir / "read_trace.expected.yaml",
    ]
    missing = [str(required) for required in required_dirs if not required.is_dir()]
    missing.extend(str(required) for required in required_files if not required.is_file())
    if missing:
        raise CheckFailure(f"{path.parent}: missing required fixture files/dirs: {', '.join(missing)}")
    return (
        load_json_compatible_yaml(fixture_dir / "call_trace.expected.yaml"),
        load_json_compatible_yaml(fixture_dir / "read_trace.expected.yaml"),
    )


def assert_preflight_blocked_does_not_generate_body(fixture: dict[str, Any]) -> None:
    route = fixture.get("expected_route", {})
    result = fixture.get("expected_result", {})
    if route.get("node_id") == "script_draft.preflight" and result.get("status") == "blocked":
        if result.get("body_generated") is not False:
            raise CheckFailure(f"{fixture['fixture_id']}: blocked preflight must set body_generated=false")
        forbidden_created = result.get("forbidden_created_artifacts", [])
        created = set(result.get("created_artifacts", []))
        leaked = created.intersection(forbidden_created)
        if leaked:
            raise CheckFailure(f"{fixture['fixture_id']}: blocked preflight created forbidden artifacts: {sorted(leaked)}")


def assert_bounded_context(fixture: dict[str, Any]) -> None:
    route = fixture.get("expected_route", {})
    if route.get("bounded_context") != "short-drama-remake":
        raise CheckFailure(f"{fixture['fixture_id']}: route must stay in short-drama-remake bounded context")


def assert_p10_anti_redundancy(fixture: dict[str, Any]) -> None:
    route = fixture.get("expected_route", {})
    trace = fixture.get("node_invocation_trace", {})
    if route.get("node_id") != "script_draft.preflight":
        return

    called = set(trace.get("called_nodes", []))
    forbidden_calls = set(trace.get("forbidden_full_node_calls", []))
    unexpected = called.intersection(FORBIDDEN_P10_FULL_NODE_CALLS)
    if unexpected:
        raise CheckFailure(f"{fixture['fixture_id']}: P10 called forbidden full nodes: {sorted(unexpected)}")

    missing_declared_forbidden = FORBIDDEN_P10_FULL_NODE_CALLS.difference(forbidden_calls)
    if "anti_redundancy" in fixture.get("category", "") and missing_declared_forbidden:
        raise CheckFailure(
            f"{fixture['fixture_id']}: anti-redundancy fixture must declare forbidden full node calls: {sorted(missing_declared_forbidden)}"
        )


def assert_blocker_contract(fixture: dict[str, Any]) -> None:
    result = fixture.get("expected_result", {})
    summary = result.get("blocking_summary")
    if result.get("status") != "blocked":
        return
    if not isinstance(summary, dict):
        raise CheckFailure(f"{fixture['fixture_id']}: blocked result requires blocking_summary")
    for field in (
        "blocker_code",
        "blocking_level",
        "affected_scope",
        "user_visible_reason",
        "recommended_next_node",
        "available_actions",
    ):
        if field not in summary:
            raise CheckFailure(f"{fixture['fixture_id']}: blocking_summary missing {field}")
    if not isinstance(summary["user_visible_reason"], str) or not summary["user_visible_reason"].strip():
        raise CheckFailure(f"{fixture['fixture_id']}: blocking_summary.user_visible_reason must be a non-empty string")
    if not isinstance(summary["recommended_next_node"], str) or not summary["recommended_next_node"].strip():
        raise CheckFailure(f"{fixture['fixture_id']}: blocking_summary.recommended_next_node must be a non-empty string")
    if not isinstance(summary["available_actions"], list) or not summary["available_actions"]:
        raise CheckFailure(f"{fixture['fixture_id']}: blocking_summary.available_actions must be a non-empty list")


def assert_required_blockers(fixture: dict[str, Any]) -> None:
    assertions = fixture.get("assertions", {})
    required = set(assertions.get("required_blockers", []))
    if not required:
        return
    summary = fixture.get("expected_result", {}).get("blocking_summary", {})
    observed = set(summary.get("additional_blocker_codes", []))
    if "blocker_code" in summary:
        observed.add(summary["blocker_code"])
    missing = required.difference(observed)
    if missing:
        raise CheckFailure(f"{fixture['fixture_id']}: missing required blocker codes: {sorted(missing)}")


def assert_read_trace_contract(fixture: dict[str, Any], expected_read_trace: dict[str, Any] | None = None) -> None:
    assertions = fixture.get("assertions", {})
    read_assertion = assertions.get("read_trace_assertion", {})
    if not isinstance(read_assertion, dict):
        read_assertion = {}

    expected_read_trace = expected_read_trace or {}
    actual_reads_list = read_assertion.get("actual_reads", [])
    if not isinstance(actual_reads_list, list):
        raise CheckFailure(f"{fixture['fixture_id']}: read_trace_assertion.actual_reads must be a list")
    actual_reads = set(actual_reads_list)
    required_reads = set(read_assertion.get("required_reads", []))
    required_reads.update(expected_read_trace.get("required_reads", []))
    missing_required = required_reads.difference(actual_reads)
    if missing_required:
        raise CheckFailure(f"{fixture['fixture_id']}: required reads missing from actual_reads: {sorted(missing_required)}")

    forbidden_reads = set(read_assertion.get("forbidden_reads_not_present", []))
    forbidden_reads.update(read_assertion.get("source_bundle_reads_not_present", []))
    forbidden_reads.update(read_assertion.get("research_note_reads_not_present", []))
    forbidden_reads.update(expected_read_trace.get("forbidden_reads_not_present", []))
    forbidden_reads.update(expected_read_trace.get("source_bundle_reads_not_present", []))
    forbidden_reads.update(expected_read_trace.get("research_note_reads_not_present", []))
    if forbidden_reads and "actual_reads" not in read_assertion:
        raise CheckFailure(f"{fixture['fixture_id']}: forbidden read assertions require explicit actual_reads")
    forbidden_hits = actual_reads.intersection(forbidden_reads)
    if forbidden_hits:
        raise CheckFailure(f"{fixture['fixture_id']}: forbidden reads present: {sorted(forbidden_hits)}")

    expected_order = read_assertion.get("expected_order", []) or expected_read_trace.get("expected_order", [])
    if expected_order:
        actual_order = actual_reads_list
        positions: list[int] = []
        for required_path in expected_order:
            try:
                positions.append(actual_order.index(required_path))
            except ValueError as exc:
                raise CheckFailure(f"{fixture['fixture_id']}: expected ordered read missing: {required_path}") from exc
        order_is_valid = positions == sorted(positions)
        if read_assertion.get("expected_order_violation") is True:
            if order_is_valid:
                raise CheckFailure(f"{fixture['fixture_id']}: expected read order violation was not present")
        elif not order_is_valid:
            raise CheckFailure(f"{fixture['fixture_id']}: actual_reads do not match expected read order")

    if read_assertion.get("enforce_default_forbidden_script_reads") is True:
        default_hits = actual_reads.intersection(DEFAULT_FORBIDDEN_SCRIPT_READS)
        if default_hits:
            raise CheckFailure(f"{fixture['fixture_id']}: default forbidden script reads present: {sorted(default_hits)}")
        prefix_hits = sorted(
            path
            for path in actual_reads
            if any(path.startswith(prefix) for prefix in DEFAULT_FORBIDDEN_READ_PREFIXES)
        )
        if prefix_hits:
            raise CheckFailure(f"{fixture['fixture_id']}: default forbidden read prefixes present: {prefix_hits}")


def assert_call_trace_contract(fixture: dict[str, Any], expected_call_trace: dict[str, Any]) -> None:
    trace = fixture.get("node_invocation_trace", {})
    called = set(trace.get("called_nodes", []))
    expected_called = set(expected_call_trace.get("called_nodes", []))
    missing_called = expected_called.difference(called)
    if missing_called:
        raise CheckFailure(f"{fixture['fixture_id']}: expected called nodes missing: {sorted(missing_called)}")

    checker_log = set(trace.get("checker_call_log", []))
    required_log = set(expected_call_trace.get("checker_call_log_contains", []))
    missing_log = required_log.difference(checker_log)
    if missing_log:
        raise CheckFailure(f"{fixture['fixture_id']}: checker_call_log missing entries: {sorted(missing_log)}")

    consumed = set(trace.get("consumed_report_ids", []))
    required_consumed = set(expected_call_trace.get("consumed_report_ids", []))
    missing_consumed = required_consumed.difference(consumed)
    if missing_consumed:
        raise CheckFailure(f"{fixture['fixture_id']}: expected consumed report ids missing: {sorted(missing_consumed)}")

    consumed_artifacts = set(trace.get("consumed_artifact_ids", []))
    required_consumed_artifacts = set(expected_call_trace.get("consumed_artifact_ids", []))
    missing_consumed_artifacts = required_consumed_artifacts.difference(consumed_artifacts)
    if missing_consumed_artifacts:
        raise CheckFailure(
            f"{fixture['fixture_id']}: expected consumed artifact ids missing: {sorted(missing_consumed_artifacts)}"
        )

    forbidden = set(expected_call_trace.get("forbidden_full_node_calls_not_present", []))
    forbidden_hits = called.intersection(forbidden)
    if forbidden_hits:
        raise CheckFailure(f"{fixture['fixture_id']}: forbidden call trace nodes present: {sorted(forbidden_hits)}")


def assert_report_consumption(fixture: dict[str, Any]) -> None:
    assertions = fixture.get("assertions", {})
    anti_redundancy = assertions.get("anti_redundancy_assertion", {})
    trace = fixture.get("node_invocation_trace", {})

    required = set(anti_redundancy.get("required_consumed_report_ids", []))
    if required:
        consumed = set(trace.get("consumed_report_ids", []))
        missing = required.difference(consumed)
        if missing:
            raise CheckFailure(f"{fixture['fixture_id']}: required report ids were not consumed: {sorted(missing)}")

    expected_packet_id = anti_redundancy.get("resume_packet_consumed")
    if expected_packet_id:
        packet = fixture.get("initial_project_state", {}).get("runtime_packet", {})
        actual_packet_id = packet.get("packet_id")
        if actual_packet_id != expected_packet_id:
            raise CheckFailure(
                f"{fixture['fixture_id']}: expected resume packet {expected_packet_id}, got {actual_packet_id}"
            )


def assert_transaction_contract(fixture: dict[str, Any]) -> None:
    assertions = fixture.get("assertions", {}).get("transaction_assertion", {})
    if not assertions:
        return

    status = assertions.get("transaction_status")
    if status not in {"committed", "rolled_back", "transaction_failed"}:
        raise CheckFailure(f"{fixture['fixture_id']}: transaction_assertion requires stable transaction_status")

    records = assertions.get("records", {})
    if not isinstance(records, dict):
        raise CheckFailure(f"{fixture['fixture_id']}: transaction_assertion.records must be an object")

    if assertions.get("no_half_confirmed_state") is True:
        committed = records.get("decision_log") == "committed"
        registry_updated = records.get("registry") == "updated"
        artifact_updated = records.get("artifact_status") == "updated"
        if len({committed, registry_updated, artifact_updated}) > 1 and status != "transaction_failed":
            raise CheckFailure(f"{fixture['fixture_id']}: half-confirmed state must be transaction_failed")

    if status == "transaction_failed":
        allowed = {"transaction_failed", "rolled_back", "not_written"}
        invalid = {name: value for name, value in records.items() if value not in allowed}
        if invalid:
            raise CheckFailure(f"{fixture['fixture_id']}: transaction_failed has inconsistent records: {invalid}")


def assert_fast_confirmed_invalidation(fixture: dict[str, Any]) -> None:
    assertions = fixture.get("assertions", {}).get("fast_confirmed_assertion", {})
    if not assertions:
        return

    if assertions.get("mode_before") != "fast_confirmed":
        raise CheckFailure(f"{fixture['fixture_id']}: fast fixture must start with fast_confirmed mode")
    invalidators = set(assertions.get("invalidated_by", []))
    if not invalidators.intersection({"dirty", "needs_sync"}):
        raise CheckFailure(f"{fixture['fixture_id']}: fast_confirmed must be invalidated by dirty or needs_sync")
    if assertions.get("mode_after") != "invalidated":
        raise CheckFailure(f"{fixture['fixture_id']}: fast_confirmed dirty/needs_sync must end as invalidated")


def assert_phase5_specific_contracts(fixture: dict[str, Any]) -> None:
    fixture_id = fixture.get("fixture_id", "")
    summary = fixture.get("expected_result", {}).get("blocking_summary", {})
    blocker_code = summary.get("blocker_code")

    if fixture_id == "p9_gate_blocks_unverified_claim" and blocker_code != "FACT_GATE_BLOCKED":
        raise CheckFailure(f"{fixture_id}: expected blocker_code FACT_GATE_BLOCKED")
    if fixture_id == "partial_source_forbids_full_claim" and blocker_code != "SOURCE_SCOPE_PARTIAL_FORBIDS_FULL_CLAIM":
        raise CheckFailure(f"{fixture_id}: expected blocker_code SOURCE_SCOPE_PARTIAL_FORBIDS_FULL_CLAIM")
    if fixture_id == "research_notes_not_directly_read_by_script":
        read_assertion = fixture.get("assertions", {}).get("read_trace_assertion", {})
        if "research-notes.md" not in read_assertion.get("research_note_reads_not_present", []):
            raise CheckFailure(f"{fixture_id}: must assert research-notes.md is not directly read")


def assert_postflight_contract(fixture: dict[str, Any]) -> None:
    route = fixture.get("expected_route", {})
    result = fixture.get("expected_result", {})
    assertions = fixture.get("assertions", {}).get("postflight_assertion", {})
    report = result.get("postflight_report")

    if route.get("node_id") != "script_draft.postflight" and not report and not assertions:
        return
    if not isinstance(report, dict):
        raise CheckFailure(f"{fixture['fixture_id']}: postflight fixture requires expected_result.postflight_report")

    report_status = report.get("report_status")
    if report_status not in POSTFLIGHT_REPORT_STATUSES:
        raise CheckFailure(f"{fixture['fixture_id']}: invalid postflight report_status: {report_status}")

    expected_report_status = assertions.get("expected_report_status")
    if expected_report_status and report_status != expected_report_status:
        raise CheckFailure(
            f"{fixture['fixture_id']}: expected postflight report_status {expected_report_status}, got {report_status}"
        )

    leaked_registry_fields = sorted(POSTFLIGHT_REGISTRY_OWNED_FIELDS.intersection(report.keys()))
    if leaked_registry_fields:
        raise CheckFailure(
            f"{fixture['fixture_id']}: postflight_report contains registry-owned fields: {leaked_registry_fields}"
        )

    if report_status == "passed":
        required_values = {
            "quality_gate_status": "passed",
            "user_review_status": "accepted",
            "canon_commit_status": "committed",
            "state_update_status": "updated",
            "next_episode_unlock_status": "unlocked",
        }
        mismatches = {
            field: report.get(field)
            for field, expected in required_values.items()
            if report.get(field) != expected
        }
        if mismatches:
            raise CheckFailure(f"{fixture['fixture_id']}: postflight passed with failing substatuses: {mismatches}")

        read_trace_diff = report.get("read_trace_diff", {})
        risk_recheck = report.get("risk_recheck", {})
        sync_check = report.get("sync_check", {})
        if read_trace_diff.get("clean") is not True:
            raise CheckFailure(f"{fixture['fixture_id']}: postflight passed requires read_trace_diff.clean=true")
        if risk_recheck.get("status") != "passed":
            raise CheckFailure(f"{fixture['fixture_id']}: postflight passed requires risk_recheck.status=passed")
        if sync_check.get("status") != "passed":
            raise CheckFailure(f"{fixture['fixture_id']}: postflight passed requires sync_check.status=passed")
        memorable_moment = report.get("memorable_moment_check", {})
        if memorable_moment.get("status") != "passed":
            raise CheckFailure(f"{fixture['fixture_id']}: postflight passed requires memorable_moment_check.status=passed")
        moment = str(memorable_moment.get("moment", "")).strip()
        if not moment:
            raise CheckFailure(f"{fixture['fixture_id']}: postflight passed requires a concrete memorable moment")
    else:
        if result.get("downstream_unlocked") is not False:
            raise CheckFailure(f"{fixture['fixture_id']}: non-passed postflight must set downstream_unlocked=false")
        if report.get("next_episode_unlock_status") == "unlocked":
            raise CheckFailure(f"{fixture['fixture_id']}: non-passed postflight cannot unlock next episode")
        forbidden_created = set(result.get("forbidden_created_artifacts", []))
        created = set(result.get("created_artifacts", []))
        leaked = created.intersection(forbidden_created)
        if leaked:
            raise CheckFailure(f"{fixture['fixture_id']}: non-passed postflight created forbidden artifacts: {sorted(leaked)}")

    trace = fixture.get("node_invocation_trace", {})
    consumed_reports = set(trace.get("consumed_report_ids", []))
    consumed_artifacts = set(trace.get("consumed_artifact_ids", []))
    required_reports = set(assertions.get("required_consumed_report_ids", []))
    required_artifacts = set(assertions.get("required_consumed_artifact_ids", []))

    missing_reports = required_reports.difference(consumed_reports)
    if missing_reports:
        raise CheckFailure(f"{fixture['fixture_id']}: postflight required reports missing: {sorted(missing_reports)}")

    missing_artifacts = required_artifacts.difference(consumed_artifacts)
    if missing_artifacts:
        raise CheckFailure(f"{fixture['fixture_id']}: postflight required artifacts missing: {sorted(missing_artifacts)}")


def assert_three_layer_control_contract(fixture: dict[str, Any]) -> None:
    assertions = fixture.get("assertions", {}).get("three_layer_control_assertion", {})
    if not assertions:
        return

    result = fixture.get("expected_result", {})
    boundary = result.get("three_layer_control_boundary")
    if not isinstance(boundary, dict):
        raise CheckFailure(f"{fixture['fixture_id']}: three_layer_control_boundary is required")

    blocking_layers = set(boundary.get("blocking_layers", []))
    warning_layers = set(boundary.get("warning_layers", []))
    unknown_layers = (blocking_layers | warning_layers).difference(CONTROL_LAYERS)
    if unknown_layers:
        raise CheckFailure(f"{fixture['fixture_id']}: unknown control layers: {sorted(unknown_layers)}")

    if assertions.get("preflight_blocks_only_foundation_or_skeleton") is True:
        invalid_blockers = blocking_layers.difference({"foundation", "skeleton"})
        if invalid_blockers:
            raise CheckFailure(
                f"{fixture['fixture_id']}: preflight cannot hard-block on layers: {sorted(invalid_blockers)}"
            )

    required_free_zones = set(assertions.get("required_free_zones", []))
    free_zones = set(boundary.get("free_zones", []))
    missing_free_zones = required_free_zones.difference(free_zones)
    if missing_free_zones:
        raise CheckFailure(f"{fixture['fixture_id']}: missing free zones: {sorted(missing_free_zones)}")

    if assertions.get("requires_memorable_moment_question") is True:
        questions = set(boundary.get("postflight_questions", []))
        if "memorable_moment" not in questions:
            raise CheckFailure(f"{fixture['fixture_id']}: postflight questions must include memorable_moment")


def assert_market_adaptation_contract(fixture: dict[str, Any]) -> None:
    assertions = fixture.get("assertions", {}).get("market_adaptation_assertion", {})
    if not assertions:
        return

    route = fixture.get("expected_route", {})
    result = fixture.get("expected_result", {})
    trace = fixture.get("node_invocation_trace", {})
    route_node = route.get("node_id")
    target_market = assertions.get("target_market")
    source_market = assertions.get("source_market")
    requires_market_adaptation = assertions.get("requires_market_adaptation")
    if requires_market_adaptation is None:
        requires_market_adaptation = target_market == "overseas" or (
            bool(source_market) and bool(target_market) and source_market != target_market
        )

    if assertions.get("overseas_command_report_only") is True:
        if route_node != "market_adapt.validate":
            raise CheckFailure(f"{fixture['fixture_id']}: /仿写 出海 must route to market_adapt.validate")
        if route.get("normalized_intent") != "validate_target_market_adaptation":
            raise CheckFailure(
                f"{fixture['fixture_id']}: market_adapt.validate route must use normalized_intent "
                "validate_target_market_adaptation"
            )
        if result.get("body_generated") is not False:
            raise CheckFailure(f"{fixture['fixture_id']}: /仿写 出海 must not generate script body")
        forbidden_created = set(result.get("forbidden_created_artifacts", []))
        created = set(result.get("created_artifacts", []))
        leaked = created.intersection(forbidden_created)
        if leaked:
            raise CheckFailure(f"{fixture['fixture_id']}: /仿写 出海 created forbidden artifacts: {sorted(leaked)}")
        report = result.get("market_adaptation_report")
        if not isinstance(report, dict):
            raise CheckFailure(f"{fixture['fixture_id']}: /仿写 出海 must expose expected_result.market_adaptation_report")
        missing_report_fields = REQUIRED_MARKET_ADAPTATION_REPORT_FIELDS.difference(report.keys())
        if missing_report_fields:
            raise CheckFailure(
                f"{fixture['fixture_id']}: market_adaptation_report missing fields: {sorted(missing_report_fields)}"
            )

    if assertions.get("overseas_concepts_from_start") is True:
        if route_node != "concept.generate":
            raise CheckFailure(f"{fixture['fixture_id']}: /仿写 出海 without selected concept must route to concept.generate")
        if route.get("normalized_intent") != "generate_skin_swap_concepts":
            raise CheckFailure(
                f"{fixture['fixture_id']}: concept.generate route must use normalized_intent generate_skin_swap_concepts"
            )
        created = set(result.get("created_artifacts", []))
        expected_artifact = assertions.get("expected_concept_artifact", "02_concepts/concepts-overseas.md")
        if expected_artifact not in created:
            raise CheckFailure(f"{fixture['fixture_id']}: overseas concept artifact missing: {expected_artifact}")
        forbidden_created = set(result.get("forbidden_created_artifacts", []))
        leaked = created.intersection(forbidden_created)
        if leaked:
            raise CheckFailure(f"{fixture['fixture_id']}: overseas concept stage created forbidden artifacts: {sorted(leaked)}")
        concept_fields = set(assertions.get("required_overseas_concept_fields", []))
        if not concept_fields.issuperset(
            {
                "target_market",
                "layer_classification",
                "overseas_genre_promise",
                "source_mechanisms_to_replace",
                "paywall_pressure",
            }
        ):
            raise CheckFailure(f"{fixture['fixture_id']}: overseas concept fixture must assert core overseas fields")

    if assertions.get("forbid_short_drama_overseas_reads") is True:
        read_assertion = fixture.get("assertions", {}).get("read_trace_assertion", {})
        actual_reads = set(read_assertion.get("actual_reads", []))
        leaked_reads = sorted(path for path in actual_reads if path.startswith("short-drama/references/overseas/"))
        if leaked_reads:
            raise CheckFailure(f"{fixture['fixture_id']}: remake market adaptation read short-drama overseas refs: {leaked_reads}")

    if not requires_market_adaptation or route_node not in MARKET_ADAPTATION_REQUIRED_NODES:
        return

    report_status = assertions.get("market_adaptation_report_status", "missing")
    if report_status in {"missing", "stale", "blocked"}:
        if result.get("status") != "blocked":
            raise CheckFailure(f"{fixture['fixture_id']}: missing/stale market adaptation report must block {route_node}")
        summary = result.get("blocking_summary", {})
        if summary.get("blocker_code") != "MARKET_ADAPTATION_MISSING_OR_STALE":
            raise CheckFailure(f"{fixture['fixture_id']}: expected blocker_code MARKET_ADAPTATION_MISSING_OR_STALE")
        if result.get("body_generated") is not False:
            raise CheckFailure(f"{fixture['fixture_id']}: market adaptation block must set body_generated=false")
        created = set(result.get("created_artifacts", []))
        forbidden_created = set(result.get("forbidden_created_artifacts", []))
        leaked = created.intersection(forbidden_created)
        if leaked:
            raise CheckFailure(f"{fixture['fixture_id']}: market adaptation block created forbidden artifacts: {sorted(leaked)}")
        if summary.get("recommended_next_node") != "market_adapt.validate":
            raise CheckFailure(f"{fixture['fixture_id']}: market adaptation block must recommend market_adapt.validate")
    elif report_status == "passed":
        consumed = set(trace.get("consumed_report_ids", []))
        if "market_adaptation_report" not in consumed:
            raise CheckFailure(f"{fixture['fixture_id']}: passed market adaptation report must be consumed by {route_node}")
    else:
        raise CheckFailure(f"{fixture['fixture_id']}: unknown market_adaptation_report_status {report_status!r}")


def check_fixture(path: Path) -> list[str]:
    fixture = load_json_compatible_yaml(path)
    assert_required_fields(fixture, path)
    expected_call_trace, expected_read_trace = assert_required_fixture_files(path)
    assert_bounded_context(fixture)
    assert_preflight_blocked_does_not_generate_body(fixture)
    assert_p10_anti_redundancy(fixture)
    assert_blocker_contract(fixture)
    assert_required_blockers(fixture)
    assert_call_trace_contract(fixture, expected_call_trace)
    assert_read_trace_contract(fixture, expected_read_trace)
    assert_report_consumption(fixture)
    assert_transaction_contract(fixture)
    assert_fast_confirmed_invalidation(fixture)
    assert_phase5_specific_contracts(fixture)
    assert_postflight_contract(fixture)
    assert_three_layer_control_contract(fixture)
    assert_market_adaptation_contract(fixture)
    return [f"ok fixture {fixture['fixture_id']}"]


def run_self_test() -> list[str]:
    synthetic = {
        "fixture_id": "self_test_missing_outline",
        "title": "self test",
        "problem_refs": ["P10"],
        "category": "script_preflight",
        "initial_project_state": {},
        "user_input": {"text": "继续写第 12 集"},
        "expected_route": {
            "normalized_intent": "draft_episode_script",
            "node_id": "script_draft.preflight",
            "bounded_context": "short-drama-remake",
        },
        "expected_result": {
            "status": "blocked",
            "body_generated": False,
            "created_artifacts": [],
            "forbidden_created_artifacts": ["05_scripts/episodes/ep012.md"],
            "blocking_summary": {
                "blocker_code": "EXECUTION_CARD_MISSING",
                "blocking_level": "episode",
                "affected_scope": ["episode_012_script"],
                "user_visible_reason": "缺少第 12 集写作执行卡，不能直接生成正文。",
                "recommended_next_node": "execution_card.prepare",
                "available_actions": ["补齐本集写作执行卡", "返回分集大纲节点", "暂缓正文生成"],
            },
        },
        "node_invocation_trace": {
            "called_nodes": ["script_draft.preflight"],
            "forbidden_full_node_calls": ["resume.restore", "source.validate", "reference_map.validate", "fact_gate.validate"],
        },
        "assertions": {},
    }
    assert_bounded_context(synthetic)
    assert_preflight_blocked_does_not_generate_body(synthetic)
    assert_p10_anti_redundancy(synthetic)
    assert_blocker_contract(synthetic)
    assert_required_blockers(synthetic)
    assert_read_trace_contract(synthetic)
    assert_report_consumption(synthetic)
    assert_transaction_contract(synthetic)
    assert_fast_confirmed_invalidation(synthetic)
    assert_phase5_specific_contracts(synthetic)
    assert_three_layer_control_contract(synthetic)

    forbidden_prefix_synthetic = dict(synthetic)
    forbidden_prefix_synthetic["fixture_id"] = "self_test_forbidden_short_drama_reference_prefix"
    forbidden_prefix_synthetic["assertions"] = {
        "read_trace_assertion": {
            "actual_reads": ["short-drama/references/overseas/vertical-filmability.md"],
            "enforce_default_forbidden_script_reads": True,
        }
    }
    try:
        assert_read_trace_contract(forbidden_prefix_synthetic)
    except CheckFailure:
        pass
    else:
        raise CheckFailure("self-test: short-drama/references/ prefix leak was not blocked")
    return ["ok self-test"]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check short-drama-remake deterministic gate fixtures.")
    parser.add_argument("--fixture", action="append", default=[], help="Path to a JSON-compatible YAML fixture file.")
    parser.add_argument("--schema", action="append", default=[], help="Path to a human YAML schema contract file.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in smoke test.")
    args = parser.parse_args(argv)

    messages: list[str] = []
    try:
        if args.self_test:
            messages.extend(run_self_test())
        for raw_path in args.schema:
            path = Path(raw_path)
            assert_schema_yaml_syntax(path)
            messages.append(f"ok schema {path}")
        for raw_path in args.fixture:
            messages.extend(check_fixture(Path(raw_path)))
    except CheckFailure as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if not messages:
        parser.error("provide --self-test, --schema, or at least one --fixture")
    for message in messages:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
