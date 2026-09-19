# Initial MechaGremlin validation

Local Windows verification, 2026-09-19, Python 3.12.14, PySide6 6.11.2.

```
python -m unittest discover -s tests_mechagremlin -v
Ran 13 tests
OK

python -m unittest discover -s tests_feedback -v
Ran 4 tests
OK

python -m py_compile gremlinEx.py gremlin/ui/axis_calibration.py mechagremlin/curves.py mechagremlin/studio.py
Exit 0

git diff --cached -B -M --check
Exit 0
```

The curve suite checks monotonicity, symmetry, finite inputs, deadzones, endpoint authority, and independently evaluates serialized Bezier points. Qt offscreen tests exercise export success, cancellation, failure and replacement safety, keyboard navigation, and minimum-window geometry. Calibration regressions exercise the actual class with configuration/event ports isolated; all four failed before the setter fix.

Visual review used explicit installed Segoe UI fonts with Qt offscreen rendering at 1080x730 and 780x680. The smaller window scrolls instead of overlapping. This is not a screen-reader audit or full DPI/display matrix.

Full application startup, preset import through the complete application, physical Orion 2 input, vJoy output, and WARDOGS flight remain unverified. Curve Studio is a manual authoring preview. The inherited runtime and configuration storage remain in place; this first patch is not the complete redesign.
