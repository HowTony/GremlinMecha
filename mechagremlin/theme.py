# SPDX-License-Identifier: GPL-3.0-or-later
"""Visual tokens for MechaGremlin's native editing workspace."""
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"
PALETTE = {"base": "#1c2027", "panel": "#252b34", "plot": "#20262e",
           "border": "#3b4653", "grid": "#303a46", "text": "#edf1f5",
           "muted": "#aebac8", "curve": "#8dced8", "accent": "#dcb980"}

STYLE = """
QWidget#curveStudio, QWidget#studioContent, QScrollArea#studioScroll { background: #1c2027; color: #edf1f5; border: none; }
QWidget#curveStudio { font-family: 'Segoe UI'; font-size: 13px; }
QWidget#curveStudio QLabel { color: #edf1f5; background: transparent; border: none; }
QWidget#curveStudio QLabel[role="muted"] { color: #aebac8; }
QWidget#curveStudio QLabel[role="brand"] { font-size: 19px; font-weight: 700; }
QWidget#curveStudio QLabel[role="title"] { font-size: 25px; font-weight: 600; }
QWidget#curveStudio QLabel[role="section"] { font-size: 16px; font-weight: 600; }
QWidget#curveStudio QLabel[role="badge"] { color: #dcb980; background: #343029; border: 1px solid #65573f; border-radius: 12px; padding: 5px 11px; }
QWidget#curveStudio QLabel[role="accent"] { color: #dcb980; }
QWidget#curveStudio QFrame#controls, QWidget#curveStudio QFrame#previewPanel { background: #252b34; border: 1px solid #3b4653; border-radius: 10px; }
QWidget#curveStudio QFrame#readouts { background: #20262e; border: 1px solid #3b4653; border-radius: 8px; }
QWidget#curveStudio QLabel[role="reading"] { font-size: 29px; font-weight: 600; }
QWidget#curveStudio QLabel#outputReading { color: #8dced8; }
QWidget#curveStudio QPushButton { background: #303844; color: #edf1f5; border: 1px solid #4c5968; border-radius: 5px; padding: 9px 12px; }
QWidget#curveStudio QPushButton:hover { background: #3a4553; }
QWidget#curveStudio QPushButton:checked { background: #4c4233; border-color: #dcb980; color: #ffe0ae; }
QWidget#curveStudio QPushButton:focus { border: 2px solid #dcb980; padding: 8px 11px; }
QWidget#curveStudio QPushButton[primary="true"] { background: #dcb980; color: #20242a; border-color: #dcb980; font-weight: 600; padding: 10px 18px; }
QWidget#curveStudio QPushButton[primary="true"]:hover { background: #ebcb96; }
QWidget#curveStudio QPushButton[primary="true"]:focus { border: 2px solid #ffffff; padding: 9px 17px; }
QWidget#curveStudio QDoubleSpinBox { background: #1e242c; color: #edf1f5; border: 1px solid #506072; border-radius: 5px; padding: 8px; padding-right: 25px; font-size: 17px; }
QWidget#curveStudio QDoubleSpinBox:focus { border: 2px solid #dcb980; padding: 7px; padding-right: 24px; }
QWidget#curveStudio QDoubleSpinBox::up-button, QWidget#curveStudio QDoubleSpinBox::down-button { background: #36414e; width: 24px; border-left: 1px solid #506072; }
QWidget#curveStudio QDoubleSpinBox::up-button { subcontrol-origin: border; subcontrol-position: top right; border-top-right-radius: 4px; }
QWidget#curveStudio QDoubleSpinBox::down-button { subcontrol-origin: border; subcontrol-position: bottom right; border-bottom-right-radius: 4px; }
QWidget#curveStudio QDoubleSpinBox::up-arrow { image: url(@ASSETS@/chevron-up.svg); width: 12px; height: 12px; }
QWidget#curveStudio QDoubleSpinBox::down-arrow { image: url(@ASSETS@/chevron-down.svg); width: 12px; height: 12px; }
QWidget#curveStudio QSlider::groove:horizontal { height: 5px; background: #536170; border-radius: 2px; }
QWidget#curveStudio QSlider::sub-page:horizontal { background: #8dced8; }
QWidget#curveStudio QSlider::handle:horizontal { background: #edf1f5; border: 2px solid #252b34; width: 18px; margin: -8px 0; border-radius: 10px; }
QWidget#curveStudio QSlider:focus { border: 1px solid #dcb980; border-radius: 4px; }
QWidget#curveStudio QScrollBar:vertical { background: #20262e; width: 12px; margin: 0; }
QWidget#curveStudio QScrollBar::handle:vertical { background: #647589; min-height: 32px; border: 3px solid #20262e; border-radius: 5px; }
QWidget#curveStudio QScrollBar::add-line:vertical, QWidget#curveStudio QScrollBar::sub-line:vertical { height: 0; }
QWidget#curveStudio QScrollBar::add-page:vertical, QWidget#curveStudio QScrollBar::sub-page:vertical { background: none; }
QToolTip { background: #edf1f5; color: #20262e; border: 1px solid #647589; padding: 6px; }
""".replace("@ASSETS@", ASSETS.as_posix())
