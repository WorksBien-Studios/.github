# WorksBien Release Operations

This is the operating guide every WorksBien iOS app repo should carry. New apps should be created from `WorksBien-Studios/ios-app-template`, which already includes these files and workflows.

## What GitHub Can Do

After the one-time Apple setup is complete, GitHub can:

- build and upload a new TestFlight build;
- deliver the exact processed build to the mapped beta group;
- attach the exact build to the matching App Store version;
- upload App Store listing metadata;
- upload declared screenshot/image PNGs;
- submit the exact build for App Review when explicitly authorized.

## One-Time Apple Setup

Before a repo can push anything real, create or verify these Apple records:

| Apple record | Copy into |
| --- | --- |
| Explicit Bundle ID | `APP_IDENTITY.json -> app.bundle_id` |
| App Store Connect app ID | `APP_IDENTITY.json -> app.asc_app_id` |
| SKU | `APP_IDENTITY.json -> app.sku` |
| Apple team ID | `APP_IDENTITY.json -> app.team_id` |
| TestFlight beta group ID | `APP_IDENTITY.json -> release.beta_group_id` |
| Support URL | `APP_IDENTITY.json -> listing.support_url` |
| Privacy URL | `APP_IDENTITY.json -> listing.privacy_url` |
| EULA URL | every locale `eula_url` and public description |

## Repo Setup

1. Edit `APP_IDENTITY.json`.
2. Generate the release files:

   ```bash
   python3 scripts/materialize_release_contract.py
   python3 scripts/materialize_release_contract.py --check
   ```

3. Commit the generated files:
   - `.github/testflight-app-map.json`
   - `docs/app-store-listing-manifest.json`
4. Grant the repo access to the selected org secrets:
   - `ASC_ISSUER_ID`
   - `ASC_KEY_ID`
   - `ASC_PRIVATE_KEY`
5. Confirm the org variables are visible:
   - `ASC_EXPECTED_ISSUER_ID`
   - `ASC_EXPECTED_KEY_ID`
6. Run the `Release contract` workflow.
7. Switch `release_state` to `ready` only when all Apple IDs and Xcode paths are real.

## Push TestFlight

Use the repo workflow:

```text
Actions -> TestFlight -> Run workflow
```

The workflow calls:

```text
WorksBien-Studios/.github/.github/workflows/ios-testflight.yml@main
```

It will fail closed if:

- the app map is not `state: "ready"`;
- the app map repository does not match the repo;
- the App Store Connect app ID or bundle ID is wrong;
- the org key ID or issuer ID does not match the expected variables;
- the exact-SHA build check named by `required_check_name` has not passed.

Do not put listing upload, screenshots, or review submission into the TestFlight workflow.

## Push Listing Metadata

Use the repo workflow:

```text
Actions -> App Store listing and review submission -> Run workflow
operation = upload_listing
upload_screenshots = false
```

The workflow calls:

```text
WorksBien-Studios/.github/.github/workflows/ios-app-store.yml@main
```

Before metadata upload, the manifest must pass:

- `source_control.fact_ledger_complete = true`;
- `source_control.facts_reconciled = true`;
- every locale has supported claims;
- every locale has support, privacy, and EULA URLs;
- every public description includes the exact EULA URL;
- `compliance_controls.legal_urls_live.status = "pass"`.

## Push Screenshots Or Images

Use the same App Store workflow with:

```text
operation = upload_listing
upload_screenshots = true
```

Every screenshot entry in `docs/app-store-listing-manifest.json` must declare:

- `locale`
- `device`
- `position`
- `artifact_path`
- `width`
- `height`

The PNG must exist in the repo and match the declared width and height. These gates must also be true:

- `authentic_ui`
- `dimensions_verified_against_current_apple_spec`
- `display_appearance_checked`
- `localized_copy_checked`
- `claims_supported`
- `no_other_platform_imagery`

## Submit For Review

Only use review submission after the user explicitly authorizes final submission.

Run:

```text
operation = submit_review
build_number = exact processed build number
confirm_submission = true
```

The manifest must also have:

- `mode = "submission"`;
- `authorization.live_submission_authorized = true`;
- `human_review.attested = true`;
- `review.contact_complete = true`;
- all compliance controls set to `pass` or `n_a`.

## New Repo Checklist

For every new WorksBien iOS repo:

- start from `WorksBien-Studios/ios-app-template`;
- keep this document at `docs/worksbien-release-operations.md`;
- keep `APP_IDENTITY.json` as the only manually edited release identity source;
- keep the `Release contract`, `TestFlight`, and `App Store listing and review submission` workflows;
- do not grant Apple secrets until the app identity points to the correct Apple records;
- keep listing and screenshot pushes separate from TestFlight pushes.
