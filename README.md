# WorksBien release automation

This repository is the organization-level release harness for WorksBien Studios iOS apps.

## What is centralized

- Reusable TestFlight delivery workflow: `.github/workflows/ios-testflight.yml`
- Reusable App Store listing/submission workflow: `.github/workflows/ios-app-store.yml`
- Starter workflow templates for app repos: `workflow-templates/`
- Shared App Store Connect helpers: `scripts/asc_jwt.rb` and `scripts/asc_delivery.rb`
- Listing/screenshot gate: `scripts/validate_listing_manifest.py`
- Bootstrap and guardrail docs: `docs/app-store-connect-bootstrap.md`, `docs/release-secret-access.md`, and `docs/app-store-listing-gates.md`

The app repos should call the reusable workflows through `@main` so central release fixes apply without per-repo SHA churn.

## Default new-repo path

Create new iOS apps from the public template repository:

- `WorksBien-Studios/ios-app-template`

The template includes the workflow callers, a canonical `APP_IDENTITY.json`, generated TestFlight/App Store files, and a sync check. For a new app, edit `APP_IDENTITY.json`, run `python3 scripts/materialize_release_contract.py`, commit the generated files, and switch `release_state` to `ready` only after the App Store Connect IDs, Xcode scheme/container, beta group, and listing data are real.

## New iOS repo checklist

1. Prefer creating the repository from `WorksBien-Studios/ios-app-template`.
2. If retrofitting an existing repository, add `.github/testflight-app-map.json` from `templates/testflight-app-map.example.json`.
3. If retrofitting an existing repository, add `docs/app-store-listing-manifest.json` from `templates/app-store-listing-manifest.example.json`.
4. Add the WorksBien starter workflows from GitHub Actions:
   - WorksBien iOS TestFlight
   - WorksBien App Store listing and submission
5. Ensure the repo has a successful exact-SHA CI check whose name matches `required_check_name`.
6. Confirm the App Store Connect app ID, bundle ID, beta group ID, team ID, and marketing version match across:
   - `.github/testflight-app-map.json`
   - `docs/app-store-listing-manifest.json`
   - Xcode project settings
   - App Store Connect
7. Keep listing submission blocked until the manifest has `mode: "submission"`, human review is attested, and live submission is explicitly authorized.

## Automatic lane contract

The lane fails closed when:
- the requested SHA is not exact;
- the app map is not `state: ready`;
- the App Store Connect key/issuer does not match the org variables;
- the manifest app ID, bundle ID, or version does not match the release map;
- exact-SHA CI has not passed;
- screenshots are requested but not fully declared and verified;
- review submission is requested without explicit manifest authorization.

GitHub cannot inject workflow files into every brand-new repository by itself. For truly automatic new repos, create apps from a template repository that already contains the two caller workflows, the app-map placeholder, and the listing manifest placeholder.
