# Foxglove API and SDK integration

## Run the offline replay

From a VEAP source checkout install the optional dependencies with `python -m pip install -e '.[foxglove,test]'`. Run:

```sh
python -m veap.adapters.foxglove_replay --tape artifacts/research/v06-control-tape.json --trace artifacts/research/v06-mujoco-locked-replay.json --trace artifacts/research/v06-isaaclab-locked-replay.json --out replay.mcap
python -m pytest -q tests/test_foxglove_integration.py
```

Open replay.mcap locally in Foxglove. Select /veap/mujoco/physics or /veap/isaaclab/physics in Raw Messages. Plot position_xyz_m[0] against playback time for each topic. Log timestamps represent simulation-relative nanoseconds; they must not be interpreted as original UTC capture dates. Each channel records the tape and input file digests. Preserve the source JSON for VEAP verifier input. The export is custom JSON telemetry; it does not substitute for ROS 2 CDR odometry.

## Read project recording metadata

With FOXGLOVE_TOKEN supplied through the operator environment, use `python -m veap.adapters.foxglove_recordings --project PROJECT_ID --limit 100`. This optional backend adapter emits JSON lines. It preserves timestamp strings to nanosecond precision, handles offset pagination and bounded 429 retries, and propagates access failures. Results are a paginated view of current metadata; concurrent server updates can affect ordering across pages. The official Python API client is distributed as foxglove-client and imported as foxglove.client.Client. VEAP uses a small HTTP adapter here to control the precise timestamp serialization and retry policy. No keys enter Next.js or the native RL loop.

## Acceptance register

| Surface | Contract or required verification | Status |
|---|---|---|
| Authentication | Test capability-specific grants, organization keys, PAT restrictions, endpoint-specific OAuth grants, project selection and ProjectLimitedCredentialDenied. Use the endpoint-specific Site Bucket Notifications contract. | Recording reader uses a bearer token and explicit project. Hosted identity tests pending. |
| Sorting, pagination, timestamps, limits | Endpoint-specific sort fields; default/maximum 2000 where supported; UTC Z, up to nine fractional digits; handle 429 and Retry-After. | Recording reader and offline response tests. |
| Automations | Test owner/project context, plan entitlement, member management versus organization-key execution of saved instructions. | Pending |
| Coverage, Topics, Stream data | Verify available time ranges, schema discovery and seek/stream boundaries on an imported fixture. | Pending |
| Custom Properties, Events, Event Types, Sessions, Devices | Typed metadata, validation, device-to-time linkage, retention and filters. | Pending |
| Recordings, Recording Attachments, Imports, Lake files | Use Recordings for new work. Verify scoped metadata, attachment digest/download, imported Primary Site state and self-hosted enterprise lake access. Imports is deprecated. | Recording list implemented; others pending. |
| Episodes, Datasets | Only eligible Primary Site recordings; same-site membership, effective edits/versioning, draft commit/discard/restore and immutable manifests for ML splits. | Pending |
| Projects, Sites | Verify tenant and project boundaries, multi-project explicit selection, global site operation denial and plan support. | Pending |
| Device Tokens, Site Tokens, Site Inbox Notification Tokens | Separate credential kinds, capability checks, rotation, revocation and project-limited restrictions. | Pending |
| Webhooks, Webhook Payloads | Verify supported event payloads, authenticity, delivery idempotency and tenant binding. | Pending |
| Extensions, Layouts | Validate authenticated, project-aware distribution and layout restore against a pinned schema. | Pending |
| SDK installation, concepts, examples, logging strategies, schemas | Python custom JSON channels to MCAP implemented. Add native C++ logging outside the RL control loop; compare queue pressure, dropped samples and P95 inference latency. Add Rust verifier-side consumption. | Python file path exercised. C++/Rust SDK paths pending. |
| WebSocket Server and Remote Access Gateway | Verify live subscriptions against file replay, reconnect, authorization, and credentials at remote boundary. | Pending |

Sources: https://docs.foxglove.dev/api , https://docs.foxglove.dev/docs/sdk , https://docs.foxglove.dev/docs/sdk/logging-messages , https://github.com/foxglove/foxglove-sdk .
