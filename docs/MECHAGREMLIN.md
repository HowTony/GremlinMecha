# MechaGremlin redesign brief

## Audience and purpose

People connecting flight controls, driving controls, accessibility hardware, and custom panels should be able to produce a working mapping without learning the application's internals. Experienced users must retain access to modes, conditions, plugins, and advanced routing.

## Design direction

A native Qt desktop application with a persistent device list, a focused mapping workspace, and contextual tuning. Use progressive disclosure: common controls first, advanced tools within reach. Represent physical input, transformation, and game output as distinct stages. Never imply a device is connected or a mapping is active without runtime evidence.

Palette: navy #172333, slate #213247, border #455b70, foreground #eef4fa, muted text #b5c7d8, cyan curve #6cdae2. Segoe UI provides native Windows legibility and accessibility. Large graphs carry the visual identity; keep surrounding controls quiet. Sentence case, descriptive buttons, visible keyboard focus, and text alongside status color.

## Implemented first slice

Curve Studio is a native QDialog, also runnable separately. It presents a bounded symmetric cubic curve and center deadzone, with manual preview and atomic XML preset export. The exact cubic is represented by two Bezier segments in the inherited preset format. The input/output math is pure Python and tested independently of Qt and device drivers. The app's Tools menu opens the studio, and its runtime title identifies MechaGremlin.

## Remaining milestones

1. Establish full runtime/build baseline on supported Windows configurations; test actual controller and vJoy output, profile loading, reconnects, and start/stop. Identify dependency/version drift before changing the input engine.
2. Device setup workflow: detect devices, ask users to move an axis, calibrate with visible evidence, assign a role, show the output mapping, and validate endpoints.
3. Main workspace redesign: device sidebar, searchable mappings, contextual inspector, clear active/inactive state, and full keyboard navigation. Preserve advanced editing while introducing the simpler flow.
4. Connect Curve Studio to selected physical inputs and profile commands, with undoable edits, live readings, and a reversible comparison between two settings.
5. Profile library: explicit backups, import review, device substitution, and game associations. Keep unverified presets clearly labeled.
6. Independent packaging and update identity, isolated configuration storage with explicit migration, accessibility/DPI checks, hardware regression suite, and a public release.

## Engineering boundaries

Keep the inherited input engine until measured evidence justifies a change. UI rendering must not block input dispatch. Measure processing time separately from game response. No smoothing enabled by default; curve shape cannot undo delay inside a game. Never replace profile identifiers through broad branding search-and-replace.

Maintain an upstream remote and focused commits. Retain license and attribution. Track remaining GremlinEx branding as part of the packaging milestone rather than changing protocol/module identifiers blindly.

## Current verification limits

Pure curve behavior, serialized control points, Qt interactions, and offscreen layout can be checked without drivers. Actual preset import through the complete runtime, controller output, full application boot, and the installer require separate verification. Do not describe this initial slice as a finished product.

## Research behind the work

Three parallel reviews cover [original Joystick Gremlin](feedback-original-gremlin.md), [GremlinEx](feedback-gremlinex.md), and [SimAppPro setup](feedback-setup.md). Each separates firsthand complaints from reproduced bugs and features already present in Ex.

The first confirmed inherited bug fix is calibration's maximum deadzone becoming uneditable after zero. Four regression cases fail against the old setter and pass with a value-comparison guard. Curve Studio also confirms the final export filename before replacing it and supports keyboard navigation.

Independent export review verified the XML structure against the inherited parser and the Bezier representation against its spline evaluator. The control points represent the intended cubic exactly; the inherited evaluator uses a sampled lookup, with a measured maximum normalized error below 0.000075 in the reviewed sweep. That is not a measurement of hardware latency or flight response.

Known inherited import limitation: loading a curve preset preserves its symmetric values but the existing editor may leave its symmetry lock disabled. Enable the symmetry control before manual point edits if mirrored editing is desired. A full import/UI regression belongs in the integration milestone.
