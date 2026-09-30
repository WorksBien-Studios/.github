# App Store Connect Bootstrap

Use this once for each new iOS app before switching `APP_IDENTITY.json` from draft to ready.

## Apple setup

Create or verify these Apple records:

| Item | Where | Copy into |
| --- | --- | --- |
| Explicit Bundle ID | Apple Developer Certificates, Identifiers & Profiles | `app.bundle_id` |
| App Store Connect app | App Store Connect My Apps | `app.asc_app_id` |
| SKU | App Store Connect app information | `app.sku` |
| Apple team ID | Developer account membership | `app.team_id` |
| Internal beta group | App Store Connect TestFlight | `release.beta_group_id` |
| Privacy policy URL | Public website | `listing.privacy_url` |
| Support URL | Public website | `listing.support_url` |
| EULA URL | Apple standard EULA or approved custom URL | every locale `eula_url` and description |

## Repository setup

1. Create the repo from `WorksBien-Studios/ios-app-template`.
2. Add the Xcode project or workspace.
3. Edit `APP_IDENTITY.json`.
4. Run:

```bash
python3 scripts/materialize_release_contract.py
python3 scripts/materialize_release_contract.py --check
```

5. Commit the generated files.
6. Grant the repo access to `ASC_ISSUER_ID`, `ASC_KEY_ID`, and `ASC_PRIVATE_KEY`.
7. Run the `Release contract` workflow.
8. Switch `release_state` to `ready` only when the generated map and Apple records agree.

## Store delivery setup

Before `upload_listing`:

- Complete supported claims for every locale.
- Include the EULA URL in every public description.
- Set `legal_urls_live` to `pass` only after opening support, privacy, marketing, and EULA URLs.
- If uploading screenshots, declare every screenshot PNG with width and height.

Before `submit_review`:

- Attach an exact processed TestFlight build.
- Set `mode: "submission"`.
- Set `live_submission_authorized` and `human_review.attested` to true.
- Confirm reviewer contact details are complete in App Store Connect.
