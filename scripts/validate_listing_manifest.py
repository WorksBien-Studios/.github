#!/usr/bin/env python3
"""Fail-closed WorksBien App Store listing, legal, and screenshot gates."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import struct
import sys
from typing import Any
from urllib.parse import urlparse

APPLE_STANDARD_EULA = "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class GateError(Exception):
    pass


def load_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise GateError(f"{path} is not valid JSON: {exc}") from exc


def ensure_inside(root: pathlib.Path, path: pathlib.Path, label: str) -> pathlib.Path:
    resolved = path.resolve()
    if resolved != root and root not in resolved.parents:
        raise GateError(f"{label} is outside the repository: {path}")
    return resolved


def as_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def require_https(url: str, label: str) -> None:
    parsed = urlparse(url)
    require(parsed.scheme == "https" and bool(parsed.netloc), f"{label} must be a complete HTTPS URL.")


def text_bytes(value: Any) -> int:
    return len(str(value or "").encode("utf-8"))


def read_png_size(path: pathlib.Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        signature = handle.read(8)
        require(signature == PNG_SIGNATURE, f"{path} is not a PNG file.")
        length_bytes = handle.read(4)
        chunk_type = handle.read(4)
        require(chunk_type == b"IHDR" and len(length_bytes) == 4, f"{path} is missing a PNG IHDR header.")
        width, height = struct.unpack(">II", handle.read(8))
        require(width > 0 and height > 0, f"{path} has invalid PNG dimensions.")
        return width, height


def validate_locale(locale: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    code = str(locale.get("locale", "")).strip() or "<missing locale>"

    required_text = ("name", "subtitle", "description", "support_url", "privacy_url")
    for field in required_text:
        if not str(locale.get(field, "")).strip():
            problems.append(f"{code}: {field} is required")

    limits = {
        "name": 30,
        "subtitle": 30,
        "promotional_text": 170,
        "description": 4000,
        "whats_new": 4000,
    }
    for field, limit in limits.items():
        value = str(locale.get(field, "") or "")
        if len(value) > limit:
            problems.append(f"{code}: {field} exceeds {limit} characters")

    keywords = locale.get("keywords", [])
    if isinstance(keywords, list):
        keywords_text = ",".join(str(item).strip() for item in keywords if str(item).strip())
    else:
        keywords_text = str(keywords or "").strip()
    if text_bytes(keywords_text) > 100:
        problems.append(f"{code}: keywords exceed 100 UTF-8 bytes")

    for field in ("support_url", "marketing_url", "privacy_url"):
        value = str(locale.get(field, "") or "").strip()
        if value:
            try:
                require_https(value, f"{code}: {field}")
            except GateError as exc:
                problems.append(str(exc))

    eula_url = str(locale.get("eula_url", "") or "").strip()
    description = str(locale.get("description", "") or "")
    if not eula_url:
        problems.append(f"{code}: eula_url is required")
    else:
        try:
            require_https(eula_url, f"{code}: eula_url")
        except GateError as exc:
            problems.append(str(exc))
        if eula_url not in description:
            problems.append(f"{code}: description must include eula_url so the public listing exposes the EULA")

    if not locale.get("claims_supported"):
        problems.append(f"{code}: claims_supported must be true before delivery")

    return problems


def validate_screenshots(root: pathlib.Path, manifest: dict[str, Any], upload_screenshots: bool) -> list[str]:
    problems: list[str] = []
    screenshots = manifest.get("screenshots", [])

    if upload_screenshots and not screenshots:
        return ["Screenshot upload requested but no screenshots are declared."]

    required_flags = (
        "authentic_ui",
        "dimensions_verified_against_current_apple_spec",
        "display_appearance_checked",
        "localized_copy_checked",
        "claims_supported",
        "no_other_platform_imagery",
    )

    for index, shot in enumerate(screenshots, start=1):
        prefix = f"screenshot[{index}]"
        for field in ("locale", "device", "position", "artifact_path"):
            if not str(shot.get(field, "")).strip():
                problems.append(f"{prefix}: {field} is required")

        if upload_screenshots:
            missing_flags = [flag for flag in required_flags if not shot.get(flag)]
            if missing_flags:
                problems.append(f"{prefix}: required screenshot gates are not true: {', '.join(missing_flags)}")

            source = str(shot.get("artifact_path", "")).strip()
            if source:
                path = ensure_inside(root, root / source, f"{prefix} artifact_path")
                if not path.is_file():
                    problems.append(f"{prefix}: missing screenshot artifact {source}")
                else:
                    try:
                        width, height = read_png_size(path)
                        expected_width = shot.get("width", shot.get("expected_width"))
                        expected_height = shot.get("height", shot.get("expected_height"))
                        if expected_width is None or expected_height is None:
                            problems.append(f"{prefix}: width and height must be declared")
                        elif (int(expected_width), int(expected_height)) != (width, height):
                            problems.append(
                                f"{prefix}: PNG dimensions are {width}x{height}, expected {expected_width}x{expected_height}"
                            )
                    except (GateError, ValueError) as exc:
                        problems.append(str(exc))

    return problems


def validate(args: argparse.Namespace) -> list[str]:
    root = pathlib.Path.cwd().resolve()
    manifest_path = ensure_inside(root, root / args.manifest, "manifest")
    app_map_path = ensure_inside(root, root / args.app_map, "app map")

    problems: list[str] = []
    require(manifest_path.is_file(), "Listing manifest is missing.")
    require(app_map_path.is_file(), "TestFlight app map is missing.")

    manifest = load_json(manifest_path)
    app_map = load_json(app_map_path)

    operation = args.operation
    upload_screenshots = as_bool(args.upload_screenshots)
    confirm_submission = as_bool(args.confirm_submission)

    if operation not in {"upload_listing", "submit_review"}:
        problems.append("operation must be upload_listing or submit_review")

    if app_map.get("state") != "ready":
        problems.append("app map state must be ready")
    if app_map.get("repository") != args.repo:
        problems.append("app map repository must match the caller repository")

    app = manifest.get("app", {})
    if str(app.get("app_id", "")).strip() != str(app_map.get("asc_app_id", "")).strip():
        problems.append("manifest app_id must match app map asc_app_id")
    if app.get("bundle_id") != app_map.get("bundle_id"):
        problems.append("manifest bundle_id must match app map bundle_id")
    if str(app.get("version", "")) != str(app_map.get("marketing_version", "")):
        problems.append("manifest version must match app map marketing_version")

    source = manifest.get("source_control", {})
    if not source.get("fact_ledger_complete"):
        problems.append("source_control.fact_ledger_complete must be true")
    if not source.get("facts_reconciled"):
        problems.append("source_control.facts_reconciled must be true")

    locales = manifest.get("locales", [])
    if not locales:
        problems.append("at least one locale is required")
    else:
        for locale in locales:
            problems.extend(validate_locale(locale))

    for name, control in manifest.get("compliance_controls", {}).items():
        status = control.get("status")
        if operation == "submit_review" and status not in {"pass", "n_a"}:
            problems.append(f"submission control is not cleared: {name}")
        if name == "legal_urls_live" and status != "pass":
            problems.append("legal_urls_live must be pass before metadata delivery")

    problems.extend(validate_screenshots(root, manifest, upload_screenshots))

    if operation == "submit_review":
        if not confirm_submission:
            problems.append("submit_review requires confirm_submission=true")
        if manifest.get("mode") != "submission":
            problems.append("submit_review requires manifest mode=submission")
        if not manifest.get("authorization", {}).get("live_submission_authorized"):
            problems.append("live_submission_authorized must be true")
        if not manifest.get("human_review", {}).get("attested"):
            problems.append("human_review.attested must be true")
        if not str(args.build_number or "").isdigit():
            problems.append("submit_review requires an exact numeric build_number")
        if not manifest.get("review", {}).get("contact_complete"):
            problems.append("review.contact_complete must be true")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--app-map", default=".github/testflight-app-map.json")
    parser.add_argument("--operation", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--upload-screenshots", default="false")
    parser.add_argument("--confirm-submission", default="false")
    parser.add_argument("--build-number", default="")
    args = parser.parse_args()

    try:
        problems = validate(args)
    except GateError as exc:
        problems = [str(exc)]

    if problems:
        print("WorksBien listing gate failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1

    print("WorksBien listing gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
