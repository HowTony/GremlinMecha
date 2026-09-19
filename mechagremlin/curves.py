# SPDX-License-Identifier: GPL-3.0-or-later
"""A bounded, symmetric curve with exact GremlinEx Bezier preset export."""
from dataclasses import dataclass
import math
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Curve:
    center_sensitivity: float = 0.6
    deadzone: float = 0.01

    def __post_init__(self):
        if not math.isfinite(self.center_sensitivity) or not 0 <= self.center_sensitivity <= 1:
            raise ValueError("Center sensitivity must be between 0 and 1.")
        if not math.isfinite(self.deadzone) or not 0 <= self.deadzone <= 0.25:
            raise ValueError("Deadzone must be between 0 and 0.25.")

    def output(self, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("Input must be finite.")
        magnitude = min(1.0, max(0.0, (abs(value) - self.deadzone) / (1 - self.deadzone)))
        result = self.center_sensitivity * magnitude + (1 - self.center_sensitivity) * magnitude ** 3
        return math.copysign(result, value)

    def control_points(self):
        s = self.center_sensitivity
        return [(-1, -1), (-2/3, -2*s/3), (-1/3, -s/3), (0, 0),
                (1/3, s/3), (2/3, 2*s/3), (1, 1)]

    def preset_xml(self) -> bytes:
        root = ET.Element("curve_preset")
        data = ET.SubElement(root, "curve-data", mode="diagonal", centered="True", filtered="False")
        mapping = ET.SubElement(data, "mapping", type="cubic-bezier-spline")
        for x, y in self.control_points():
            ET.SubElement(mapping, "control-point", x=repr(x), y=repr(y))
        ET.SubElement(data, "deadzone", {"low": "-1.0", "center-low": repr(-self.deadzone),
                                       "center-high": repr(self.deadzone), "high": "1.0"})
        ET.indent(root)
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)
