# WorksBien release automation

This repository is the organization-level release harness for WorksBien Studios iOS apps.

## What is centralized

- Reusable TestFlight delivery workflow: `.github/workflows/ios-testflight.yml`
- Reusable App Store listing/submission workflow: `.github/workflows/ios-app-store.yml`
- Starter workflow templates for app repos: `workflow-templates/`
- Shared App Store Connect helpers: `scripts/asc_jwt.rb` and `scripts/asc_delivery.rb`

The app repos should call the reusable workflows through `@main` so central release fixes apply without per-repo SHA churn.

## New iOS repo checklist

1. Add `.github/testflight-app-map.json` from `templates/testflight-app-map.example.json`.
2. Add `docs/app-store-listing-manifest.json` from `templates/app-store-listing-manifest.example.json`.
3. Add the WorksBien starter workflows from GitHub Actions:
   - WorksBien iOS TestFlight
   - WorksBien App Store listing and submission
4. Ensure the repo has a successful exact-SHA CI check whose name matches `required_check_name`.
5. Confirm the App Store Connect app ID, bundle ID, beta group ID, team ID, and marketing version match across:
   - `.github/testflight-app-map.json`
   - `docs/app-store-listing-manifest.json`
   - Xcode project settings
   - App Store Connect
6. Keep listing submission blocked until the manifest has `mode: "submission"`, human review is attested, and live submission is explicitly authorized.

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
