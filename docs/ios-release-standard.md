# WorksBien iOS Release Automation Standard

This organisation uses a four-part release setup for iOS apps:

1. Org-wide instructions live in this repository.
2. Org workflow templates live in `workflow-templates/`.
3. New apps should start from `WorksBien-Studios/ios-app-template`.
4. Each app owns one canonical identity file: `APP_IDENTITY.json`.

## Source of truth

For new repositories, edit `APP_IDENTITY.json` first. It materializes the two files consumed by the reusable workflows:

- `.github/testflight-app-map.json`
- `docs/app-store-listing-manifest.json`

Run this before opening release PRs:

```bash
python3 scripts/materialize_release_contract.py
python3 scripts/materialize_release_contract.py --check
```

## Required organisation configuration

These organisation-level secrets must be available to every iOS release repo that should upload builds or listings:

- `ASC_ISSUER_ID`
- `ASC_KEY_ID`
- `ASC_PRIVATE_KEY`

These organisation variables must also be available:

- `ASC_EXPECTED_ISSUER_ID`
- `ASC_EXPECTED_KEY_ID`

The reusable workflows verify the live secret values against the expected variable values before touching App Store Connect.

## Automatic lane requirements

A repo can use the automatic lanes when:

- `.github/testflight-app-map.json` has `state: "ready"`.
- `repository` exactly equals the GitHub repository full name.
- `bundle_id`, `asc_app_id`, `team_id`, `scheme`, and `xcode_container` are real.
- The Xcode project or workspace exists at `xcode_container`.
- The CI check named by `required_check_name` succeeds for the exact release SHA.
- The listing manifest app ID and bundle ID match the TestFlight app map.

## Submission guardrails

Listing upload and final App Review submission are intentionally separate.

- `operation: upload_listing` uploads metadata and optional screenshots.
- `operation: submit_review` requires `listing.mode: "submission"`, human review attestation, live submission authorization, and explicit workflow confirmation.

This keeps new repositories automatic while preventing a placeholder template or stale listing file from mutating the wrong App Store Connect app.
