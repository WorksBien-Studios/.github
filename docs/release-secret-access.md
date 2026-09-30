# WorksBien Release Secret Access

WorksBien keeps Apple API credentials as organisation secrets and variables.

## Current policy

Use selected-repository access for production App Store Connect credentials unless an owner explicitly changes the risk posture.

Required organisation secrets:

- `ASC_ISSUER_ID`
- `ASC_KEY_ID`
- `ASC_PRIVATE_KEY`

Required organisation variables:

- `ASC_EXPECTED_ISSUER_ID`
- `ASC_EXPECTED_KEY_ID`

## New repository access path

For each new iOS repository created from `WorksBien-Studios/ios-app-template`:

1. Complete `APP_IDENTITY.json`.
2. Generate and commit the release files.
3. Add the repository to the selected-repository access list for all three `ASC_*` secrets.
4. Confirm the org variables are visible to the repository.
5. Run the `Release contract` workflow.
6. Run TestFlight only after the app map is `state: "ready"`.

## Full automatic option

If WorksBien later chooses maximum automation over secret minimization, switch each `ASC_*` organisation secret to all repositories. That makes every current and future org repo able to request App Store Connect credentials, so it should be paired with branch protection and required release gates.
