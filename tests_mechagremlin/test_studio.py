# SPDX-License-Identifier: GPL-3.0-or-later
"""Offscreen Qt interaction and file-safety regressions; no hardware required."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PySide6 import QtCore, QtGui, QtTest, QtWidgets
from mechagremlin.studio import CurveStudio


class StudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        # Offscreen Qt on Windows may not discover installed fonts by itself.
        for font in ("segoeui.ttf", "segoeuib.ttf", "seguisb.ttf"):
            path = Path("C:/Windows/Fonts") / font
            if path.is_file():
                QtGui.QFontDatabase.addApplicationFont(str(path))

    def setUp(self):
        self.window = CurveStudio()
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.addCleanup(self.window.close)
        self.addCleanup(self.window.deleteLater)

    def export(self, path):
        with patch.object(QtWidgets.QFileDialog, "getSaveFileName", return_value=(str(path), "")):
            self.window.export_preset()

    def test_unsuffixed_existing_export_requires_confirmation_and_no_preserves_file(self):
        path = Path(self.folder.name) / "curve.xml"
        path.write_bytes(b"existing curve")
        with patch.object(QtWidgets.QMessageBox, "question", return_value=QtWidgets.QMessageBox.StandardButton.No) as ask:
            self.export(path.with_suffix(""))
        self.assertEqual(path.read_bytes(), b"existing curve")
        self.assertIn(str(path), ask.call_args.args[2])
        self.assertEqual(ask.call_args.args[-1], QtWidgets.QMessageBox.StandardButton.No)

    def test_confirmed_existing_export_writes_valid_preset(self):
        path = Path(self.folder.name) / "curve.xml"
        path.write_bytes(b"existing curve")
        with patch.object(QtWidgets.QMessageBox, "question", return_value=QtWidgets.QMessageBox.StandardButton.Yes):
            self.export(path)
        self.assertEqual(path.read_bytes(), self.window.curve().preset_xml())
        self.assertIn("Saved", self.window.status.text())

    def test_new_export_adds_extension_without_confirmation(self):
        path = Path(self.folder.name) / "curve"
        with patch.object(QtWidgets.QMessageBox, "question") as ask:
            self.export(path)
        ask.assert_not_called()
        self.assertEqual(path.with_suffix(".xml").read_bytes(), self.window.curve().preset_xml())

    def test_cancel_dialog_does_not_report_success(self):
        before = self.window.status.text()
        with patch.object(QtWidgets.QFileDialog, "getSaveFileName", return_value=("", "")):
            self.window.export_preset()
        self.assertEqual(self.window.status.text(), before)

    def test_export_failure_is_visible_and_not_reported_as_saved(self):
        before = self.window.status.text()
        with patch.object(QtWidgets.QMessageBox, "warning") as warning:
            self.export(Path(self.folder.name) / "missing" / "curve.xml")
        warning.assert_called_once()
        self.assertEqual(self.window.status.text(), before)

    def test_small_window_scrolls_without_overlap_and_keyboard_reaches_export(self):
        self.window.resize(780, 680)
        self.window.show()
        self.app.processEvents()
        self.assertGreater(self.window.scroll.verticalScrollBar().maximum(), 0)
        self.assertLess(self.window.graph.geometry().bottom(), self.window.input_reading.geometry().top())
        for button in self.window.presets.values():
            self.assertGreaterEqual(button.height(), button.minimumSizeHint().height())
        self.window.presets["Linear"].setFocus()
        for _ in range(6):
            QtTest.QTest.keyClick(self.app.focusWidget(), QtCore.Qt.Key.Key_Tab)
        self.app.processEvents()
        self.assertIs(self.app.focusWidget(), self.window.export_button)
        viewport = self.window.scroll.viewport()
        button_rect = QtCore.QRect(self.window.export_button.mapTo(viewport, QtCore.QPoint()), self.window.export_button.size())
        self.assertTrue(viewport.rect().contains(button_rect))

    def test_keyboard_moves_preview_and_updates_numeric_readout(self):
        slider = self.window.test_input
        slider.setFocus()
        QtTest.QTest.keyClick(slider, QtCore.Qt.Key.Key_End)
        self.assertEqual(slider.value(), 1000)
        self.assertIn("+100.0%", self.window.output_reading.text())
        QtTest.QTest.keyClick(slider, QtCore.Qt.Key.Key_Home)
        self.assertEqual(slider.value(), -1000)
        self.assertIn("-100.0%", self.window.output_reading.text())

    def test_sensitivity_presets_keep_deadzone_and_do_not_become_enter_default(self):
        self.window.deadzone.setValue(3.5)
        self.window.presets["Soft"].click()
        self.assertEqual(self.window.sensitivity.value(), 35)
        self.assertEqual(self.window.deadzone.value(), 3.5)
        for button in [*self.window.presets.values(), self.window.export_button]:
            self.assertFalse(button.autoDefault())
        for field in (self.window.sensitivity, self.window.deadzone):
            self.assertNotIn("&", field.accessibleName())


if __name__ == "__main__":
    unittest.main()
