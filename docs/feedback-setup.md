# Setup feedback: SimAppPro and the MechaGremlin boundary

Research date: 2026-09-19. These are qualitative reports, not a ranking, prevalence estimate, or proof that a current version reproduces an old fault. MechaGremlin does not modify SimAppPro or device firmware.

## Findings and practical response

| Evidence | Bounded finding | MechaGremlin response |
| --- | --- | --- |
| [Firsthand SimAppPro remapping complaint](https://www.reddit.com/r/winwing_sim/comments/1o48fxd/simapppro_is_insanely_confusing/) (October 2025) | The author expected local button remapping and a visual device diagram, but encountered game-specific profile options. Replies disagreed about responsibility for the game's button limit. This supports a discoverability problem; it does not establish that SimAppPro should implement a virtual joystick. | Design around a clearly identified input, transformation, and output. Make local configuration possible before selecting a game. Future device diagrams need accurate hardware-specific assets and mapping data. |
| [Firsthand calibration report](https://www.reddit.com/r/hoggit/comments/yrubad/) (November 2022, follow-up February 2025) | The author could not see the expected correction after calibration. A later commenter reported relief after removing Windows calibration data. This is anecdotal and does not justify recommending registry deletion or universal resets. | Future diagnostics should show which layer is being measured, observed range, center, and processed output. Keep manufacturer calibration and software response curves distinct. |
| [Firsthand Ursa Minor calibration discussion](https://www.reddit.com/r/WinWing/comments/1p4sw7x/ursa_minor_calibration/) (late 2025 / early 2026) | Users described calibration settings changing with game-specific records and reported mixed success deleting records. This concerns a different WINWING product from Orion 2, so do not apply those steps blindly. | Surface active profile and transform chain, explain what a change affects, and make backups/recovery obvious. Do not silently change manufacturer records. |
| [Fenix official calibration guide](https://support.fenixsim.com/hc/en-us/articles/14119688746255-WinWing-WinCTRL-URSA-Minor-32-Throttle-32-PAC-Metal-Configuration-and-Calibration-Guide) (updated March 2026) | The vendor explicitly separates SimAppPro calibration, simulator bindings, and aircraft calibration. Multiple setup layers are real, even when the software behaves correctly. | Onboarding should explain each layer and its ownership, rather than imply that editing a curve completes all setup. This guide is specific to Ursa Minor/Fenix, not WARDOGS. |

## Implemented in this pass

Curve Studio stays native Qt and explicitly describes its slider as a manual preview. The graph now says **Preview output**, avoiding the suggestion that it measures live game output. Sensitivity presets describe their value and preservation of the deadzone.

Keyboard access uses mnemonic labels for sensitivity, deadzone, test position, and export. Tab order follows the page. Preset/export buttons do not become implicit Enter defaults while a number is edited. The preview slider supports arrow keys and Home/End; this is described beside the control.

Export confirms replacement of the actual final filename after adding `.xml`. Previously the native dialog could confirm an unsuffixed filename while the code subsequently overwrote an existing suffixed file. Confirmation defaults to **No**, and the existing atomic `QSaveFile` write remains in place. Cancel and error paths do not announce a successful save.

## Verification and limits

`python -m unittest discover -s tests_mechagremlin -v`: 13 tests passed in this pass, including eight native Qt offscreen tests for cancellation, explicit replacement, suffix collision, failed export, keyboard movement, preset behavior, and minimum-window layout/keyboard scrolling. Offscreen tests exercise logic/interactions, not proof of real display quality or full accessibility. No hardware, vJoy routing, screen reader, or WARDOGS flight test was performed. Live range diagnostics, device diagrams, guided binding, and driver setup are future work; the manual preview does not implement them.

Small-window follow-up: Curve Studio now uses a native scroll area with content minimum layout constraints. At 780x680 the page scrolls instead of overlapping the graph or clipping controls. The regression verifies non-overlapping graph/readout geometry and keyboard tab navigation to a fully visible export button. Explicit Windows font loading was used for inspecting the minimum-size screenshot.
