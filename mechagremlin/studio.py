# SPDX-License-Identifier: GPL-3.0-or-later
"""Native curve authoring, usable without initializing a hardware driver."""
import sys
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from mechagremlin.curves import Curve

PALETTE = {"base": "#172333", "panel": "#213247", "border": "#455b70",
           "text": "#eef4fa", "muted": "#b5c7d8", "curve": "#6cdae2"}
STYLE = """
QWidget#curveStudio { background: #172333; color: #eef4fa; }
QWidget#curveStudio QScrollArea, QWidget#curveStudio QWidget#studioContent { background: #172333; border: none; }
QWidget#curveStudio QLabel { color: #eef4fa; background: transparent; }
QWidget#curveStudio QLabel[role="muted"] { color: #b5c7d8; }
QWidget#curveStudio QLabel[role="brand"] { font-size: 23px; font-weight: 700; }
QWidget#curveStudio QLabel[role="title"] { font-size: 30px; font-weight: 600; }
QWidget#curveStudio QLabel[role="reading"] { font-size: 26px; font-weight: 600; }
QWidget#curveStudio QFrame#controls { background: #213247; border-radius: 12px; }
QWidget#curveStudio QPushButton { background: #2d4258; color: #eef4fa; border: 1px solid #455b70; border-radius: 6px; padding: 9px 14px; }
QWidget#curveStudio QPushButton:hover { background: #3a536c; }
QWidget#curveStudio QPushButton:focus { border: 2px solid #6cdae2; }
QWidget#curveStudio QPushButton[primary="true"] { background: #6cdae2; color: #10252b; font-weight: 600; }
QWidget#curveStudio QDoubleSpinBox { background: #172333; color: #eef4fa; border: 1px solid #455b70; border-radius: 5px; padding: 6px; }
QWidget#curveStudio QDoubleSpinBox:focus { border: 2px solid #6cdae2; }
QWidget#curveStudio QSlider::groove:horizontal { height: 5px; background: #455b70; border-radius: 2px; }
QWidget#curveStudio QSlider::sub-page:horizontal { background: #6cdae2; }
QWidget#curveStudio QSlider::handle:horizontal { background: #eef4fa; border: 2px solid #172333; width: 17px; margin: -7px 0; border-radius: 9px; }
QWidget#curveStudio QSlider:focus { border: 1px solid #6cdae2; }
"""


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
        self.setMinimumSize(320, 280)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.setAccessibleName("Response curve graph; numeric input and output are shown below")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        bounds = QtCore.QRectF(48, 24, self.width() - 72, self.height() - 72)

        def point(x, y):
            return QtCore.QPointF(bounds.left() + (x + 1) * bounds.width() / 2,
                                 bounds.bottom() - (y + 1) * bounds.height() / 2)

        for n in range(-4, 5):
            value = n / 4
            painter.setPen(QtGui.QPen(QtGui.QColor(PALETTE["border"]), 1 if n == 0 else 0.5))
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
        self.setFont(QtGui.QFont("Segoe UI", 10))
        self.setStyleSheet(STYLE)
        self.resize(1080, 730)
        self.setMinimumSize(780, 680)
        viewport_layout = QtWidgets.QVBoxLayout(self)
        viewport_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.scroll.setAccessibleName("Curve Studio content")
        self.content = QtWidgets.QWidget()
        self.content.setObjectName("studioContent")
        outer = QtWidgets.QVBoxLayout(self.content)
        outer.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinimumSize)
        self.scroll.setWidget(self.content)
        viewport_layout.addWidget(self.scroll)
        outer.setContentsMargins(28, 20, 28, 20)
        outer.setSpacing(16)
        header = QtWidgets.QHBoxLayout()
        header.addWidget(label("MechaGremlin", "brand"))
        header.addStretch()
        header.addWidget(label("Curve Studio  /  Preview", "muted"))
        outer.addLayout(header)
        outer.addWidget(label("Find your feel.", "title"))
        outer.addWidget(label("Make small corrections easier while keeping full control at the ends of your stick.", "muted"))
        body = QtWidgets.QHBoxLayout()
        body.setSpacing(28)
        controls = QtWidgets.QFrame()
        controls.setObjectName("controls")
        controls.setFixedWidth(290)
        settings = QtWidgets.QVBoxLayout(controls)
        settings.setContentsMargins(20, 20, 20, 20)
        settings.setSpacing(12)
        settings.addWidget(label("Centered axes", "brand"))
        settings.addWidget(label("For pitch, roll, and rudder. Keep your throttle linear to start.", "muted"))
        preset_row = QtWidgets.QHBoxLayout()
        self.presets = {}
        for name, sensitivity in (("Linear", 100), ("Gentle", 60), ("Soft", 35)):
            button = QtWidgets.QPushButton("&" + name)
            button.setAutoDefault(False)
            button.setAccessibleName(name + " sensitivity preset")
            button.setToolTip(f"Set center sensitivity to {sensitivity}%. Keeps your deadzone unchanged.")
            button.clicked.connect(lambda checked=False, s=sensitivity: self.sensitivity.setValue(s))
            preset_row.addWidget(button)
            self.presets[name] = button
        settings.addLayout(preset_row)
        self.sensitivity = self._number(settings, "Center &sensitivity", 0, 100, 60)
        settings.addWidget(label("Lower values soften small movements. 100% keeps the response linear before the deadzone.", "muted"))
        self.deadzone = self._number(settings, "Center &deadzone", 0, 25, 1)
        settings.addWidget(label("Only increase this if your controller sends input while resting at center.", "muted"))
        settings.addStretch()
        settings.addWidget(label("Full travel always reaches 100%. No smoothing or extra delay is added by this curve.", "muted"))
        body.addWidget(controls)
        preview = QtWidgets.QVBoxLayout()
        preview.setSpacing(12)
        preview.addWidget(label("Response preview"))
        preview.addWidget(label("Solid cyan: your curve     Dashed: linear reference", "muted"))
        self.graph = CurveGraph()
        preview.addWidget(self.graph, 1)
        values = QtWidgets.QHBoxLayout()
        self.input_reading = label("", "reading")
        self.output_reading = label("", "reading")
        values.addWidget(self.input_reading)
        values.addWidget(self.output_reading)
        preview.addLayout(values)
        preview.addWidget(label("Test movement manually — this preview does not read your hardware.", "muted"))
        self.test_input = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.test_input.setRange(-1000, 1000)
        self.test_input.setValue(250)
        self.test_input.setAccessibleName("Preview input position")
        self.test_input.setTickInterval(250)
        movement_caption = label("&Test position (arrow keys move; Home/End reach full travel)", "muted")
        movement_caption.setBuddy(self.test_input)
        preview.addWidget(movement_caption)
        preview.addWidget(self.test_input)
        body.addLayout(preview, 1)
        outer.addLayout(body, 1)
        footer = QtWidgets.QHBoxLayout()
        self.status = label("Export, then load the preset in an axis curve editor. Your active profile is unchanged.", "muted")
        footer.addWidget(self.status, 1)
        self.export_button = QtWidgets.QPushButton("&Export curve preset")
        self.export_button.setAutoDefault(False)
        self.export_button.setProperty("primary", True)
        self.export_button.clicked.connect(self.export_preset)
        footer.addWidget(self.export_button)
        outer.addLayout(footer)
        outer.addWidget(label("Built on GremlinEx by muchimi and Joystick Gremlin by WhiteMagic. GPL-3.0-or-later.", "muted"))
        for widget in (self.sensitivity, self.deadzone, self.test_input):
            widget.valueChanged.connect(self.refresh)
        tab_order = [*self.presets.values(), self.sensitivity, self.deadzone, self.test_input, self.export_button]
        for first, second in zip(tab_order, tab_order[1:]):
            self.setTabOrder(first, second)
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
        self.input_reading.setText(f"Input  {self.graph.input_value * 100:+.1f}%")
        self.output_reading.setText(f"Output  {self.graph.curve.output(self.graph.input_value) * 100:+.1f}%")
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
