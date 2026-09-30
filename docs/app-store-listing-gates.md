# App Store Listing And Screenshot Gates

The central App Store workflow runs `scripts/validate_listing_manifest.py` before Fastlane can touch App Store Connect.

## Metadata gates

Every delivery manifest must pass these checks:

- `.github/testflight-app-map.json` has `state: "ready"` and matches the caller repository.
- Manifest `app_id`, `bundle_id`, and `version` match the TestFlight app map.
- `source_control.fact_ledger_complete` and `source_control.facts_reconciled` are true.
- Every locale has name, subtitle, description, support URL, privacy URL, and `eula_url`.
- The public description includes the exact `eula_url`.
- `legal_urls_live` is `pass` before metadata delivery.
- App Store field limits are enforced for name, subtitle, promotional text, description, What's New, and keyword bytes.

## Screenshot gates

When `upload_screenshots=true`, every screenshot entry must declare:

- `locale`
- `device`
- `position`
- `artifact_path`
- `width`
- `height`

The file must exist in the repository, be a PNG, and match the declared dimensions. These booleans must also be true:

- `authentic_ui`
- `dimensions_verified_against_current_apple_spec`
- `display_appearance_checked`
- `localized_copy_checked`
- `claims_supported`
- `no_other_platform_imagery`

## Submission gates

`submit_review` additionally requires:

- `mode: "submission"`
- `confirm_submission=true`
- numeric `build_number`
- `authorization.live_submission_authorized=true`
- `human_review.attested=true`
- `review.contact_complete=true`
- all compliance controls are `pass` or `n_a`

These checks intentionally happen before upload or submission so bad metadata fails locally instead of mutating the wrong App Store Connect listing.
