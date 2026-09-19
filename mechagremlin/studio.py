# SPDX-License-Identifier: GPL-3.0-or-later
"""Native curve authoring, usable without initializing a hardware driver."""
import sys
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from mechagremlin.curves import Curve

from mechagremlin.theme import ASSETS, PALETTE, STYLE


def label(text, role=None):
    widget = QtWidgets.QLabel(text)
    widget.setWordWrap(True)
    if role:
        widget.setProperty("role", role)
    return widget


class CurveGraph(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.curve = Curve()
        self.input_value = 0.25
        self.setMinimumSize(320, 240)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.setAccessibleName("Response curve graph; numeric input and output are shown below")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        bounds = QtCore.QRectF(48, 24, self.width() - 78, self.height() - 72)

        def point(x, y):
            return QtCore.QPointF(bounds.left() + (x + 1) * bounds.width() / 2,
                                 bounds.bottom() - (y + 1) * bounds.height() / 2)

        painter.fillRect(bounds, QtGui.QColor(PALETTE["plot"]))
        if self.curve.deadzone:
            left = point(-self.curve.deadzone, 0).x()
            right = point(self.curve.deadzone, 0).x()
            band = QtGui.QColor(PALETTE["accent"])
            band.setAlpha(28)
            painter.fillRect(QtCore.QRectF(left, bounds.top(), right-left, bounds.height()), band)
        for n in range(-4, 5):
            value = n / 4
            painter.setPen(QtGui.QPen(QtGui.QColor(PALETTE["border"] if n == 0 else PALETTE["grid"]), 1))
            painter.drawLine(point(value, -1), point(value, 1))
            painter.drawLine(point(-1, value), point(1, value))
        painter.setPen(QtGui.QPen(QtGui.QColor(PALETTE["muted"]), 1, QtCore.Qt.PenStyle.DashLine))
        painter.drawLine(point(-1, -1), point(1, 1))
        path = QtGui.QPainterPath(point(-1, self.curve.output(-1)))
        for n in range(1, 401):
            value = -1 + n / 200
            path.lineTo(point(value, self.curve.output(value)))
        painter.setPen(QtGui.QPen(QtGui.QColor(PALETTE["curve"]), 3))
        painter.drawPath(path)
        marker = point(self.input_value, self.curve.output(self.input_value))
        painter.setPen(QtGui.QPen(QtGui.QColor(PALETTE["curve"]), 1, QtCore.Qt.PenStyle.DotLine))
        painter.drawLine(point(self.input_value, -1), marker)
        painter.drawLine(point(-1, self.curve.output(self.input_value)), marker)
        painter.setBrush(QtGui.QColor(PALETTE["text"]))
        painter.setPen(QtGui.QPen(QtGui.QColor(PALETTE["base"]), 2))
        painter.drawEllipse(marker, 6, 6)
        painter.setPen(QtGui.QColor(PALETTE["muted"]))
        painter.drawText(QtCore.QRectF(0, 0, self.width(), 22), QtCore.Qt.AlignmentFlag.AlignLeft, "Preview output")
        painter.drawText(QtCore.QRectF(0, self.height()-24, self.width(), 24), QtCore.Qt.AlignmentFlag.AlignCenter, "Movement from center")
        for value in (-1, 0, 1):
            p = point(value, -1)
            painter.drawText(QtCore.QRectF(p.x()-25, p.y()+5, 50, 20), QtCore.Qt.AlignmentFlag.AlignCenter, f"{value * 100:.0f}%")
            p = point(-1, value)
            painter.drawText(QtCore.QRectF(0, p.y()-10, 42, 20), QtCore.Qt.AlignmentFlag.AlignRight, f"{value * 100:.0f}%")


class CurveStudio(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("curveStudio")
        self.setWindowTitle("MechaGremlin | Curve Studio")
        self.setWindowIcon(QtGui.QIcon(str(ASSETS / "mecha-mark.svg")))
        self.setFont(QtGui.QFont("Segoe UI", 10))
        self.setStyleSheet(STYLE)
        self.resize(1180, 810)
        self.setMinimumSize(780, 680)
        viewport_layout = QtWidgets.QVBoxLayout(self)
        viewport_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setObjectName("studioScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.scroll.setAccessibleName("Curve Studio content")
        self.content = QtWidgets.QWidget()
        self.content.setObjectName("studioContent")
        outer = QtWidgets.QVBoxLayout(self.content)
        outer.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinimumSize)
        self.scroll.setWidget(self.content)
        viewport_layout.addWidget(self.scroll)
        outer.setContentsMargins(26, 18, 26, 18)
        outer.setSpacing(18)

        header = QtWidgets.QHBoxLayout()
        header.setSpacing(10)
        mark = QtWidgets.QLabel()
        mark.setPixmap(self.windowIcon().pixmap(42, 42))
        mark.setFixedSize(42, 42)
        mark.setAccessibleName("MechaGremlin emblem")
        header.addWidget(mark)
        header.addWidget(label("MechaGremlin", "brand"))
        header.addStretch()
        badge = label("Manual preview", "badge")
        badge.setWordWrap(False)
        header.addWidget(badge)
        outer.addLayout(header)

        heading = QtWidgets.QHBoxLayout()
        title = QtWidgets.QVBoxLayout()
        title.setSpacing(4)
        title.addWidget(label("Curve Studio", "title"))
        subtitle = label("Shape the response. Keep the control.", "muted")
        subtitle.setWordWrap(False)
        title.addWidget(subtitle)
        heading.addLayout(title)
        heading.addStretch()
        outer.addLayout(heading)

        body = QtWidgets.QHBoxLayout()
        body.setSpacing(18)
        controls = QtWidgets.QFrame()
        controls.setObjectName("controls")
        controls.setFixedWidth(276)
        settings = QtWidgets.QVBoxLayout(controls)
        settings.setContentsMargins(20, 20, 20, 20)
        settings.setSpacing(14)
        settings.addWidget(label("Response settings", "section"))
        settings.addWidget(label("For centered stick and rudder axes.", "muted"))
        preset_caption = QtWidgets.QHBoxLayout()
        preset_caption.addWidget(label("Starting point"))
        preset_caption.addStretch()
        self.preset_state = label("Gentle", "accent")
        preset_caption.addWidget(self.preset_state)
        settings.addLayout(preset_caption)
        preset_row = QtWidgets.QHBoxLayout()
        preset_row.setSpacing(4)
        self.presets = {}
        self.preset_values = {"Linear": 100, "Gentle": 60, "Soft": 35}
        for name, sensitivity in self.preset_values.items():
            button = QtWidgets.QPushButton("&" + name)
            button.setAutoDefault(False)
            button.setCheckable(True)
            button.setAccessibleName(name + " sensitivity preset")
            button.setToolTip(f"Set center sensitivity to {sensitivity}%. Keeps your deadzone unchanged.")
            button.clicked.connect(lambda checked=False, s=sensitivity: self._select_preset(s))
            preset_row.addWidget(button)
            self.presets[name] = button
        settings.addLayout(preset_row)
        self.sensitivity = self._number(settings, "Center &sensitivity", 0, 100, 60)
        settings.addWidget(label("Lower values make small movements gentler. Full travel stays at 100%.", "muted"))
        self.deadzone = self._number(settings, "Center &deadzone", 0, 25, 1)
        settings.addWidget(label("Ignore a little movement at rest. Use only enough to stop drift.", "muted"))
        settings.addStretch()
        settings.addWidget(label("Symmetric response", "accent"))
        settings.addWidget(label("Both directions share the same curve. Keep your throttle linear to start.", "muted"))
        body.addWidget(controls)

        self.preview_panel = QtWidgets.QFrame()
        self.preview_panel.setObjectName("previewPanel")
        preview = QtWidgets.QVBoxLayout(self.preview_panel)
        preview.setContentsMargins(20, 18, 20, 18)
        preview.setSpacing(12)
        graph_header = QtWidgets.QHBoxLayout()
        graph_header.addWidget(label("Response curve", "section"))
        graph_header.addStretch()
        graph_header.addWidget(label("Full range preserved", "muted"))
        preview.addLayout(graph_header)
        legend = QtWidgets.QHBoxLayout()
        legend.setSpacing(8)
        for text, color, style in (("Your curve", PALETTE["curve"], "solid"),
                                   ("Linear reference", PALETTE["muted"], "dashed")):
            swatch = QtWidgets.QFrame()
            swatch.setFixedSize(24, 2)
            swatch.setStyleSheet(f"background: transparent; border: none; border-top: 2px {style} {color};")
            legend.addWidget(swatch)
            caption = label(text, "muted")
            caption.setWordWrap(False)
            legend.addWidget(caption)
            legend.addSpacing(8)
        legend.addStretch()
        preview.addLayout(legend)
        self.graph = CurveGraph()
        preview.addWidget(self.graph, 1)

        self.readouts = QtWidgets.QFrame()
        self.readouts.setObjectName("readouts")
        readings = QtWidgets.QHBoxLayout(self.readouts)
        readings.setContentsMargins(18, 12, 18, 12)
        readings.setSpacing(24)
        self.input_reading = label("", "reading")
        self.output_reading = label("", "reading")
        self.output_reading.setObjectName("outputReading")
        for caption, reading in (("Test input", self.input_reading), ("Preview output", self.output_reading)):
            column = QtWidgets.QVBoxLayout()
            column.setSpacing(2)
            column.addWidget(label(caption, "muted"))
            column.addWidget(reading)
            readings.addLayout(column, 1)
        preview.addWidget(self.readouts)

        self.test_input = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.test_input.setRange(-1000, 1000)
        self.test_input.setValue(250)
        self.test_input.setAccessibleName("Preview input position")
        self.test_input.setTickInterval(250)
        self.test_input.setMinimumHeight(24)
        movement_caption = label("&Test position", "muted")
        movement_caption.setBuddy(self.test_input)
        preview.addWidget(movement_caption)
        preview.addWidget(self.test_input)
        preview.addWidget(label("Manual input only. Arrow keys move; Home / End test full travel.", "muted"))
        body.addWidget(self.preview_panel, 1)
        outer.addLayout(body, 1)

        footer = QtWidgets.QHBoxLayout()
        footer.setSpacing(24)
        self.status = label("Export a preset, then load it in your axis curve editor. Your active profile stays unchanged.", "muted")
        footer.addWidget(self.status, 1)
        self.export_button = QtWidgets.QPushButton("&Export curve preset")
        self.export_button.setAutoDefault(False)
        self.export_button.setProperty("primary", True)
        self.export_button.clicked.connect(self.export_preset)
        footer.addWidget(self.export_button)
        outer.addLayout(footer)
        outer.addWidget(label("Built on GremlinEx and Joystick Gremlin.  GPL-3.0-or-later.", "muted"))
        for widget in (self.sensitivity, self.deadzone, self.test_input):
            widget.valueChanged.connect(self.refresh)
        tab_order = [*self.presets.values(), self.sensitivity, self.deadzone, self.test_input, self.export_button]
        for first, second in zip(tab_order, tab_order[1:]):
            self.setTabOrder(first, second)
        self.refresh()

    def _select_preset(self, sensitivity):
        self.sensitivity.setValue(sensitivity)
        # Re-assert selection even when clicking the already selected preset.
        self.refresh()

    def _number(self, layout, text, minimum, maximum, value):
        field = QtWidgets.QDoubleSpinBox()
        field.setRange(minimum, maximum)
        field.setDecimals(1)
        field.setSingleStep(1 if maximum == 100 else 0.1)
        field.setSuffix(" %")
        field.setValue(value)
        field.setAccessibleName(text.replace("&", ""))
        caption = label(text)
        caption.setBuddy(field)
        layout.addWidget(caption)
        layout.addWidget(field)
        return field

    def curve(self):
        return Curve(self.sensitivity.value()/100, self.deadzone.value()/100)

    def refresh(self):
        self.graph.curve = self.curve()
        self.graph.input_value = self.test_input.value()/1000
        self.input_reading.setText(f"{self.graph.input_value * 100:+.1f}%")
        self.output_reading.setText(f"{self.graph.curve.output(self.graph.input_value) * 100:+.1f}%")
        selected = "Custom"
        for name, value in self.preset_values.items():
            active = self.sensitivity.value() == value
            self.presets[name].setChecked(active)
            if active:
                selected = name
        self.preset_state.setText(selected)
        self.graph.update()

    def export_preset(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export curve preset", "MechaGremlin-curve.xml", "Curve presets (*.xml)",
            options=QtWidgets.QFileDialog.Option.DontConfirmOverwrite)
        if not filename:
            return
        if not filename.lower().endswith(".xml"):
            filename += ".xml"
        # Confirm the final path, including the extension we add. Letting the file
        # dialog confirm the unsuffixed name could silently replace name.xml.
        if Path(filename).exists():
            answer = QtWidgets.QMessageBox.question(
                self, "Replace curve preset?", f"Replace the existing file?\n{filename}",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No)
            if answer != QtWidgets.QMessageBox.StandardButton.Yes:
                return
        output = QtCore.QSaveFile(filename)
        data = self.curve().preset_xml()
        if not output.open(QtCore.QIODevice.OpenModeFlag.WriteOnly):
            QtWidgets.QMessageBox.warning(self, "Could not export", output.errorString())
            return
        if output.write(data) != len(data):
            message = output.errorString()
            output.cancelWriting()
            QtWidgets.QMessageBox.warning(self, "Could not export", message)
            return
        if not output.commit():
            QtWidgets.QMessageBox.warning(self, "Could not export", output.errorString())
            return
        self.status.setText(f"Saved {filename}. Load it using Load preset in the axis curve editor.")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = CurveStudio()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
