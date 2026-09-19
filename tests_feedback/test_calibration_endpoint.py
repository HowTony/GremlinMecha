# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests for upstream calibration data without loading device drivers.

Compile the actual CalibrationData class, replacing only Qt's decorator and the
configuration/event ports. No setter implementation is copied into this test.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


def load_calibration_data():
    path = Path(__file__).resolve().parents[1] / "gremlin/ui/axis_calibration.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    definition = next(node for node in tree.body
                      if isinstance(node, ast.ClassDef) and node.name == "CalibrationData")
    future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    isolated = ast.fix_missing_locations(ast.Module(body=[future, definition], type_ignores=[]))
    changed = Mock()
    config = SimpleNamespace(changed=Mock(), filter_axis_events=False, filter_axis_threshold=0.0)
    namespace = {
        "QtCore": SimpleNamespace(Slot=lambda *args: lambda method: method),
        "gremlin": SimpleNamespace(
            config=SimpleNamespace(Configuration=lambda: config),
            event_handler=SimpleNamespace(EventListener=lambda: SimpleNamespace(calibration_changed=changed)),
        ),
    }
    exec(compile(isolated, str(path), "exec"), namespace)
    return namespace["CalibrationData"], changed


class CalibrationEndpointTests(unittest.TestCase):
    def setUp(self):
        data_type, self.changed = load_calibration_data()
        self.data = data_type()

    def test_maximum_can_be_edited_after_zero(self):
        self.data.deadzone_max = 0.0
        self.data.deadzone_max = 0.8
        self.assertEqual(self.data.deadzone_max, 0.8)
        self.assertEqual(self.changed.emit.call_count, 2)

    def test_maximum_can_return_to_negative_range_after_zero(self):
        self.data.deadzone_max = 0.0
        self.data.deadzone_max = -0.2
        self.assertEqual(self.data.deadzone_max, -0.2)

    def test_unchanged_maximum_does_not_emit_change(self):
        self.data.deadzone_max = 1.0
        self.changed.emit.assert_not_called()

    def test_bulk_noncentered_deadzone_can_recover_zero_endpoint(self):
        self.data.centered = False
        self.data.deadzone = [-1.0, 0.0]
        self.data.deadzone = [-0.9, 0.7]
        self.assertEqual(self.data.deadzone, [-0.9, 0.7])


if __name__ == "__main__":
    unittest.main()