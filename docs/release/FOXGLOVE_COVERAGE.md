# VEAP workbench coverage and acceptance register

Baseline: main 13ef67e. This is a requirements inventory for the supplied Foxglove navigation snapshot, not a product compatibility declaration. Repeated reference headings are consolidated. Use official documentation as the behavioral reference; implement VEAP components independently. Record a fixture, expected outcome, implementation revision, result and limitation for each item before promoting it to supported. Default delivery is modular Next.js App Router views with explicit data adapters. FastAPI remains the backend. A native engine or SDK does not own browser layout.

## Delivery status

| Area | Present in this change or baseline | Pending acceptance |
|---|---|---|
| Frontend | Next.js routes for Observatory, Assurance Studio and native replay; legacy dashboard controllers retained as compatibility assets; separate route-specific panels and navigation components | Browser interaction and visual regression coverage of every existing workflow; retire static fallback only after parity |
| Recorded replay | Two retained native traces, common sample selector, add/remove Raw Messages and Table panels | Arbitrary files, multiple synchronized sources, precise playback transport, timestamps and missing-channel semantics |
| Source adapters | Repository contains ROS 2/MCAP, LeRobot worker and native-engine modules | End-to-end fixture for each advertised framework, codec and hardware source |
| Native learning | C17 Q-update and greedy inference, C++20 synthetic environment, trainer/evaluator and checkpoint CLI | VEAP native physics step/reset adapter, calibrated observations and reward contract, continuous policies, independently held-out environments |
| Enterprise | Existing tenancy, auth, queue, storage and migration code | External IdP, site and device policy, tenant escape, operational and restore tests for each deployed integration |
| Remaining entries below | Product requirements or interoperability targets | Each requires its own evidence; missing evidence means pending |

## Coverage by workflow

| Workstream | Requested coverage | Acceptance fixture or task |
|---|---|---|
| Entry and reference | Overview, getting started, SDK/API, changelog, examples, open a file, CLI and releases | New user opens a pinned example from a clean environment and can identify compatible versions |
| SDK and sources | Python, C++, Rust; ROS 1, ROS 2, PX4, LeRobot; custom data/schema encodings | Decode one independently generated recording per SDK/framework and compare time, frame, type and values; exercise unknown encoding |
| Hardware and robots | Luxonis OAK, RGB camera, Stereolabs ZED, SO-101 arm | Replay labelled RGB/stereo/calibration and joint-state fixtures; identify missing calibration and clock drift |
| Agents | Overview, automations, agent sidebar, local MCP, Slack, external MCP | Run a scoped read-only evidence query; test consent, denied access, replayable audit and revoked credentials |
| Connections | Live, local, cloud; data loaders and remote loader development, authentication, deployment, cloud credentials, manifest, network troubleshooting | Seek/reconnect with bounded memory; verify expired credentials, cancellation, timeouts, missing remote range and malformed manifest |
| Viewing | Playback, comparison mode, layouts, panel registry, user scripts, FoxQL, shareable links, video export, open via CLI, ROS enum annotation, controls, migration | Open same saved view at the same timestamp on two clients; verify query, enum display and redacted shared URL |
| Data platform | Import/export, devices, recordings, sessions, events, search, gallery | Ingest once, associate a device and session, retrieve event intervals, export and verify time range and hashes |
| Learning data | Datasets and episodes, manage/label episodes, manage datasets, PyTorch/Ray training, access/export | Convert time intervals to labelled episodes, seal split and provenance, round-trip export, consume in framework workers without cross-split leakage |
| Primary sites | Hosted cloud, BYOS and FAQ, on-premises, storage mode, inbox listener, indexer, query/search services, cloud credentials, management, upgrades, monitoring, autoscaling, MCAP optimization, FAQ | Exercise ingest–index–query on owned storage; rotate credentials, restore a snapshot, compare optimized MCAP payloads and record query latency |
| Edge sites | Installation, upload settings, data management, upgrades, monitoring, logging, FAQ | Record offline, reconnect, resume upload without duplicates, verify checksum, inspect logs and recover interrupted upgrade |
| Fleet | Overview, device tokens, Foxlet token lifecycle, installation, management, logging, state, FAQ; Bridge and remote access | Simulate two devices, revoke one token, reconnect the other; validate scoped remote access, rate limits and audit |
| Integration | Extensions, local development, publishing, custom panel, schema/topic converters, performance, Rust loader, user-script utility | Load version-pinned extension, exercise schema conversion and time-range request, then reject an incompatible module |
| Webhooks | Getting started and security | Verify signature, timestamp, replay rejection, retry idempotency and tenant scope |
| Embedding | TypeScript and React guides, parent-owned live transport and remote-loader transport, @foxglove/embed and @foxglove/embed-react; Jupyter and layouts; Grafana queries/troubleshooting | Embed pinned test recording in each selected host; test origin restrictions, token boundaries, empty results and transport errors |
| Administration | CLI, OAuth, personal access tokens, release feeds, settings, audit logs, pricing, standalone license, projects, roles, seat types, SSO | Build role/seat matrix, record deployment/license prerequisites and revocation outcomes; check audit export for secret leakage |

## Panels and interaction contracts

| Panels | Required behavior and test |
|---|---|
| 3D, Image, Map, Transform Tree, Topic Graph | Registered transforms and camera frames; display image annotations, maps, stale transforms and disconnected topics |
| Audio, Plot, Gauge, Indicator, State Transitions | Synchronize with transport; handle gaps, nonfinite values, units and discrete transitions |
| Raw Messages, Table, Data Source Info, Diagnostics, Log | Preserve nested values, types, timestamps, severity and missingness; inspect a source without modification |
| Markdown, Tab, Variables, Variable Slider, Parameters | Persist typed workspace state; sanitize rendered text; isolate layout variables from live device settings |
| Publish, Service Call, Teleop | Simulated endpoint with explicit scope, command preview, expiry, audit and stop behavior. Physical command authority requires a separately approved robot-control design |

Implement add by menu or drag to a specific region, panel menu/split/change/remove, move, expand/collapse, double-click title, settings focus and visible selected border. Topic sidebar supports fuzzy subsequences and quoted exact search, nested FoxQL fields, Shift range selection and Ctrl/Cmd multiselect. Drop any topic on Raw Messages or Table, images/annotations on Image, expressions on Plot or State Transitions. Support dragging from settings to duplicate a series or inspect a 3D topic. Validate incompatible drops and keyboard alternatives.

Keyboard fixtures cover comma for settings, Cmd+A to select panels, Cmd+B to close sidebar, hover + backtick shortcuts and horizontal numeric-input dragging. Import/export settings as per-panel JSON; separate whole-layout schema. Reject malformed JSON and incompatible versions without corrupting the open layout. Include accessibility, focus restoration, persistence and mobile pointer checks.

## Extension API inventory

Treat the following requested names as reference interfaces for adapter design. Native Foxglove extension binary/API compatibility is unverified. For each family, compile a typed example and run an invalid-input case, cancellation or teardown check where applicable.

| Family | Reference names |
|---|---|
| Entry and lifecycle | Entry point, ExtensionContext, ExtensionModule, ExtensionPanelRegistration, LayoutActions, PanelExtensionContext, RenderState |
| Settings | SettingsIcon, SettingsTree, SettingsTreeAction, SettingsTreeChildren, SettingsTreeField, SettingsTreeFields, SettingsTreeFieldValue, SettingsTreeNode, SettingsTreeNodeAction, SettingsTreeNodeActionDivider, SettingsTreeNodeActionItem, SettingsTreeNodeDrag |
| Subscription and ranges | SubscribeMessageRangeArgs, Subscription |
| Message converters | RegisterMessageConverterArgs, RegisterMessageConverterArgsSchema, RegisterMessageConverterArgsTopic, LegacyRegisterMessageConverterArgs |
| Aliases | BaseTopic, TopicAlias, TopicAliasFunction |
| Values, time, and messages | AppSettingValue, Immutable, MessageEvent, MessageSchemaDescription, MessageSchemaField, ParameterValue, Time, Topic, VariableStruct, VariableValue |
| Loader SDK | Rust SDK, data-loader lifecycle, range streaming and cancellation; cover interface and type-alias documentation in generated reference |

## Implementation sequence

1. Deliver native RL and Next.js foundation. Compare trained and zero policies, verify checkpoint reload and deterministic repeat; build and smoke-test routes. Synthetic environment metrics are confined to the training map.
2. Add C/C++ environment reset/step bridge to the existing physics implementation, including canonical observations, action units, reward components, termination versus truncation, time and constraint events. Replay the known command tape first; compare state against the existing native runner. Separate calibration and held-out tapes.
3. Add offline MCAP/ROS 2 adapters, topic registry, synchronized playback, persistent layouts and plugin SDK. Qualify every panel using captured multi-topic fixtures.
4. Add versioned dataset/episode manifests, multiple training seeds, held-out maps, policy export, distribution-shift checks, latency distribution and deterministic evaluation. Pin model, compiler, scenario, seed and observation schema per run.
5. Deliver edge/fleet/cloud, integration, extension and admin workstreams as individually measured milestones. Track verified/requested items, scenario coverage, denied-access tests, evidence completeness, and measured P95 latency for each workload. Publish measured denominators and environment.

Reference sources: https://docs.foxglove.dev/docs and https://docs.foxglove.dev/docs/visualization/panels . Q-learning: Watkins & Dayan (1992), https://doi.org/10.1007/BF00992698 .
