# Original Joystick Gremlin feedback: implications for MechaGremlin

Research date: 2026-09-19. Sources are firsthand reports and maintainer documentation. Reports establish user pain, not a reproduced defect in current GremlinEx. Closed issues do not alone prove a fix. Original R14 is a UI/profile rewrite; R13 reports must not be represented as current R15 defects. Ex baseline inspected: 02f1b79dab292e8f517c8073c9b09c834d520074 (the local origin/develop reference).

## 1. Startup failure leaves people reinstalling without actionable diagnosis

Original [#305](https://github.com/WhiteMagic/JoystickGremlin/issues/305) (2020, open) and [#590](https://github.com/WhiteMagic/JoystickGremlin/issues/590) (2025, open, version unclear) describe launch failure or a background process without a window. [Discussion #541](https://github.com/WhiteMagic/JoystickGremlin/discussions/541) explicitly concerns R13.3 and two vJoy devices; the maintainer identifies input-library/device visibility as a possible cause. These are recurring setup symptoms, not proof of one root cause.

Original R14.2 added startup misconfiguration messages and better vJoy handling. Ex already logs missing/disabled vJoy devices and suggests checking HidHide in gremlin/joystick_handling.py. Improvement: show a readable startup health panel with physical visibility, driver availability, output availability and precise next steps; preserve profile editing if output cannot start. Do not automatically reinstall drivers or claim every visibility failure is HidHide. Acceptance: simulated missing, busy and invisible devices yield distinct messages; none overwrites profile data.

## 2. Curves are difficult to understand and diagnose

Original [#363](https://github.com/WhiteMagic/JoystickGremlin/issues/363) (2021, closed, version unspecified) reports a nonzero resting output and explicitly asks for clearer curve documentation. The graph interpretation problem recurs in a [2022 firsthand discussion](https://www.reddit.com/r/hotas/comments/uvx0jq). We have not reproduced its numerical symptom. Original R14.3 later fixed response-curve interaction/update bugs, so the old report cannot establish that current math is broken.

Ex already has cubic/Bezier editing, preset import/export, a written interaction guide, and Input/Curved values with an axis repeater (gremlin/curve_handler.py). Improvement: explain centered stick versus one-way throttle coordinates; provide simple center sensitivity/deadzone controls alongside advanced editing; show input/output percentages and neutral behavior. Build on the existing preview instead of claiming preview is new. Acceptance: centered presets preserve zero and endpoints; throttle mode explicitly labels its rest point; export/reimport produces the same sampled curve.

## 3. Device sleep can interrupt unrelated controls

Original [#276](https://github.com/WhiteMagic/JoystickGremlin/issues/276) (2020, closed) describes an Xbox controller connection or sleep deactivating the profile. The same use case was requested in [Ex #17](https://github.com/muchimi/JoystickGremlinEx/issues/17) (2024, closed).

Ex ALREADY addresses this with runtime_ignore_device_change, default True, plus an Options checkbox. Its event handler ignores the change while running. Improvement: expose the policy and a plain-language connection status in the dashboard; distinguish an unrelated controller sleeping from a mapped HOTAS disappearing. Do not describe ignoring changes as full hotplug recovery. Acceptance: unplugging an unrelated gamepad leaves the profile active, and loss of a mapped device has a visible status. Any output-release/reacquisition redesign needs separate runtime tests.

## 4. Destructive profile edits need visible recovery

Original [#387](https://github.com/WhiteMagic/JoystickGremlin/issues/387) (2021, closed, exact release unspecified) documents removing modes and then failing to load the profile. The maintainer confirms the supplied profile had lost its modes and their data. This is historical evidence for recoverability, not a current Ex defect.

Ex ALREADY has profile backup rotation (default five), configuration backup/restore, and a confirmation explaining that mode deletion removes mappings (gremlin/base_profile.py, gremlin/config.py, gremlin/ui/dialogs.py). Original R14.1 also added save-before-close prompting. Improvement: a Recovery screen listing dated profile backups with restore-as-copy and mapping counts; show exactly how many mappings deletion affects. Acceptance: restoring does not overwrite the sole surviving original; malformed backup fails with an explanation; cancellation changes nothing.

## 5. Advanced control flow is hard to discover

Original [#71](https://github.com/WhiteMagic/JoystickGremlin/issues/71) (2017, closed) requests axis merging as an ordinary action rather than a separate dialog and describes confusing curve behavior. The maintainer's [R14 introduction](https://github.com/WhiteMagic/JoystickGremlin/blob/develop/doc/r14_intro.md) separately acknowledges confusing R13 conditions and hard-to-discover virtual buttons. R14 restructured these; this is not an assertion that original R15 retains the old layout.

Ex already implements merging in Map to vJoy, including selection and a merge repeater (action_plugins/map_to_vjoy/__init__.py). Improvement: a concise route summary that shows Physical axis -> calibration -> curve -> selected virtual axis, with mode/conditions visible; explain which transform affects a merged route. Keep advanced actions available. Acceptance: summary reflects actual configured action order and mode, and never implies a curve sends game input without an output mapping.

## Priorities

First: actionable setup diagnostics and readable routing; then approachable curve editing, followed by recovery visibility. Retain existing Ex capabilities. Hardware behavior requires on-device validation; issue research and source inspection cannot certify flight feel or prove latency improvements.

Release context: [original release notes](https://github.com/WhiteMagic/JoystickGremlin/releases) document the R14.1, R14.2, R14.3 and R15 improvements above. This report intentionally separates historical complaints, existing mitigations, and proposed improvements.
