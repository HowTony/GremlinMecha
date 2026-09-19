# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent gates: python -m unittest discover -s tests_mechagremlin -v."""
import math
import unittest
import xml.etree.ElementTree as ET
from mechagremlin.curves import Curve


class CurveTests(unittest.TestCase):
    def test_bounds_symmetry_and_monotonicity(self):
        for sensitivity in (0, 0.35, 0.6, 1):
            for deadzone in (0, 0.01, 0.25):
                curve = Curve(sensitivity, deadzone)
                values = [curve.output(x / 1000) for x in range(-1000, 1001)]
                self.assertEqual(values[0], -1)
                self.assertEqual(values[-1], 1)
                self.assertTrue(all(a <= b for a, b in zip(values, values[1:])))
                for x in (0, 0.01, 0.25, 0.5, 1):
                    self.assertAlmostEqual(curve.output(x), -curve.output(-x))
                self.assertEqual(curve.output(deadzone), 0)
                self.assertEqual(curve.output(-deadzone), 0)

    def test_linear_and_saturation(self):
        curve = Curve(1, 0)
        for x in (-1, -0.6, 0, 0.8, 1):
            self.assertEqual(curve.output(x), x)
        self.assertEqual(curve.output(2), 1)
        self.assertEqual(curve.output(-2), -1)

    def test_invalid_settings_and_input(self):
        for value in (-1, 1.1, math.inf, math.nan):
            with self.assertRaises(ValueError):
                Curve(value)
        for value in (-0.1, 0.26, math.inf, math.nan):
            with self.assertRaises(ValueError):
                Curve(deadzone=value)
        for value in (math.inf, -math.inf, math.nan):
            with self.assertRaises(ValueError):
                Curve().output(value)

    def test_export_bezier_matches_preview(self):
        # Independently evaluate the serialized cubic, rather than the export helper.
        for sensitivity in (0, 0.35, 0.6, 1):
            curve = Curve(sensitivity, 0)
            root = ET.fromstring(curve.preset_xml())
            self.assertEqual(root.tag, "curve_preset")
            data = root.find("curve-data")
            self.assertEqual(data.get("filtered"), "False")
            mapping = data.find("mapping")
            self.assertEqual(mapping.get("type"), "cubic-bezier-spline")
            points = [(float(p.get("x")), float(p.get("y"))) for p in mapping]
            self.assertEqual(len(points), 7)
            for start in (0, 3):
                segment = points[start:start+4]
                for step in range(101):
                    t = step/100
                    weights = ((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3)
                    x, y = (sum(p[axis]*w for p, w in zip(segment, weights)) for axis in (0, 1))
                    self.assertAlmostEqual(y, curve.output(x), places=12)
            zone = data.find("deadzone")
            self.assertEqual(float(zone.get("low")), -1)
            self.assertEqual(float(zone.get("high")), 1)

    def test_export_deadzone(self):
        zone = ET.fromstring(Curve(deadzone=0.02).preset_xml()).find("curve-data/deadzone")
        self.assertEqual(float(zone.get("center-low")), -0.02)
        self.assertEqual(float(zone.get("center-high")), 0.02)
