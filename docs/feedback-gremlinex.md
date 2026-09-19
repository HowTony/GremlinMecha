# GremlinEx feedback triage

Research date: 2026-09-19. Sources are first-person upstream GitHub issues,
read through the public GitHub API. Reports describe the versions in their titles;
an open issue is not proof its symptom still exists in the current development branch.

| Report | User impact | MechaGremlin response |
| --- | --- | --- |
| [#290: Input Calibration UI](https://github.com/muchimi/JoystickGremlinEx/issues/290) | Typed deadzone edits reportedly revert; inversion is difficult to understand. | Inspect calibration data setters and add regression coverage. Clearly explain input/output inversion in the redesign. |
| [#288: Input Viewer wasted space](https://github.com/muchimi/JoystickGremlinEx/issues/288) | Device selectors occupy too much width and button grids require excessive scrolling. | Prioritize a collapsible selector and adaptive monitoring layout; not implemented by this patch. |
| [#360: Problems importing profile](https://github.com/muchimi/JoystickGremlinEx/issues/360) | Repeated device prompts, no progress indication, confusion mapping another user's similar hardware. | Plan an explicit source-to-destination device review and import progress with a summary; not implemented by this patch. |
| [#348: Missing vJoy exception](https://github.com/muchimi/JoystickGremlinEx/issues/348) | Removing a problematic driver causes an unhandled exception. | Driver readiness should be visible before activating outputs. Full legacy startup still needs reproduction. |
| [#377: Reorder actions/containers](https://github.com/muchimi/JoystickGremlinEx/issues/377) | Users describe deleting and rebuilding actions to change ordering. | Investigate reorder controls with preserved IDs and undo; not implemented by this patch. |

## Confirmed fix: calibration maximum becomes stuck at zero

While investigating #290, code inspection found a distinct reproducible defect in
`CalibrationData.deadzone_max`. Its setter tested the truthiness of the old maximum.
After setting that maximum to `0.0`, every later edit was ignored. Assigning the
same nonzero value also emitted an unnecessary calibration change notification.

The setter now compares the old and new values, matching the other deadzone
setters. This fixes both direct and bulk deadzone updates. This narrow fix is not
claimed to resolve every historical symptom in #290.

Verification: `.venv\Scripts\python.exe -m unittest discover -s tests_feedback -v`.
All four regressions failed before the one-line change and passed afterward:
positive and negative edits after zero, bulk noncentered edits, and unchanged-value
notification suppression. The tests compile the actual `CalibrationData` class
from its source and replace only its Qt decorator and configuration/event ports;
they do not initialize drivers or the rest of the UI. Hardware and full-window
calibration interaction have not been verified by this test.