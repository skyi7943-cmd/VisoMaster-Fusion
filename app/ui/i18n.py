"""Small, offline Qt internationalization layer used by the main app and launcher.

The English source strings remain the canonical values used by application logic and
workspace files.  Translations are loaded from JSON and are applied only when text is
presented to the user.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from PySide6 import QtCore, QtGui, QtWidgets


LANGUAGE_ENGLISH = "en_US"
LANGUAGE_CHINESE = "zh_CN"
SUPPORTED_LANGUAGES = (LANGUAGE_CHINESE, LANGUAGE_ENGLISH)
SOURCE_TEXT_ROLE = int(QtCore.Qt.ItemDataRole.UserRole) + 198

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_PREFERENCE_PATH = _PROJECT_ROOT / "app_language.json"
_TRANSLATION_PATH = Path(__file__).resolve().parent / "translations" / "zh_CN.json"
_language = LANGUAGE_CHINESE
_translations: dict[str, str] = {}
_reverse_translations: dict[str, str] = {}
_localizer: "UiLocalizer | None" = None


def _load_translations() -> None:
    global _translations, _reverse_translations
    if _translations:
        return
    try:
        with _TRANSLATION_PATH.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
        _translations = {
            str(source): str(target)
            for source, target in data.items()
            if source and target
        }
    except (OSError, ValueError, TypeError):
        _translations = {}
    _reverse_translations = {target: source for source, target in _translations.items()}


def load_language() -> str:
    """Return the saved UI language, defaulting to Simplified Chinese."""
    try:
        with _PREFERENCE_PATH.open("r", encoding="utf-8") as stream:
            language = json.load(stream).get("language", LANGUAGE_CHINESE)
    except (OSError, ValueError, TypeError, AttributeError):
        language = LANGUAGE_CHINESE
    return language if language in SUPPORTED_LANGUAGES else LANGUAGE_CHINESE


def get_language() -> str:
    return _language


def language_option_default(_manager: Any = None) -> str:
    return "English" if get_language() == LANGUAGE_ENGLISH else "Simplified Chinese"


def language_code_from_option(option: str) -> str:
    return LANGUAGE_ENGLISH if option == "English" else LANGUAGE_CHINESE


def _source_text(text: str) -> str:
    _load_translations()
    return _reverse_translations.get(text, text)


def source_text(text: str) -> str:
    """Return the canonical English value for translated display text."""
    return _source_text(text)


def tr(text: Any) -> Any:
    """Translate an English display string without changing non-string values."""
    if not isinstance(text, str) or not text or _language == LANGUAGE_ENGLISH:
        return text
    _load_translations()
    direct = _translations.get(text)
    if direct is not None:
        return direct

    # Preserve shortcut suffixes while translating the visible action name.
    if "\t" in text:
        title, shortcut = text.split("\t", 1)
        translated_title = _translations.get(title, title)
        if translated_title != title:
            return f"{translated_title}\t{shortcut}"

    # Common runtime messages contain paths, names, counts, or error details.
    patterns: tuple[tuple[str, str], ...] = (
        (r"^Processing frame (\d+) of (\d+)$", r"正在处理第 \1/\2 帧"),
        (r"^Loading Target Media (\d+)/(\d+)$", r"正在加载目标媒体 \1/\2"),
        (r"^Loaded (\d+) of (\d+)$", r"已加载 \1/\2"),
        (r"^Found (\d+) face(?:s)?$", r"检测到 \1 张人脸"),
        (r"^Frame (\d+)$", r"第 \1 帧"),
        (r"^Failed to (.+): (.+)$", r"无法\1：\2"),
        (r"^Error: (.+)$", r"错误：\1"),
    )
    for pattern, replacement in patterns:
        if re.match(pattern, text):
            return re.sub(pattern, replacement, text)
    if text.startswith("Processing: "):
        return f"正在处理：{text.removeprefix('Processing: ')}"
    match = re.match(r"^Abort Scan \((\d+)/(\d+)\)$", text)
    if match:
        return f"中止扫描（{match.group(1)}/{match.group(2)}）"
    match = re.match(r"^Zoom - x([0-9.]+)$", text)
    if match:
        return f"缩放 - ×{match.group(1)}"
    match = re.match(r"^(.+) \(Includes K/V Maps\)$", text)
    if match:
        return f"{match.group(1)}（包含 K/V 映射）"
    return text


def set_language(language: str, *, persist: bool = True) -> None:
    """Change language and immediately refresh all currently open Qt windows."""
    global _language
    if language not in SUPPORTED_LANGUAGES:
        language = LANGUAGE_CHINESE
    _language = language
    if persist:
        try:
            with _PREFERENCE_PATH.open("w", encoding="utf-8") as stream:
                json.dump({"language": language}, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
        except OSError:
            pass
    app = QtWidgets.QApplication.instance()
    if app is not None:
        for window in app.topLevelWidgets():
            translate_object_tree(window)


def _remember_source(obj: QtCore.QObject, property_name: str, current: str) -> str:
    key = f"_i18n_source_{property_name}"
    source = obj.property(key)
    previous_translation = (
        _translations.get(source) if isinstance(source, str) else None
    )
    if not isinstance(source, str) or current not in {
        source,
        previous_translation,
        tr(source),
    }:
        source = _source_text(current)
        obj.setProperty(key, source)
    return source


def _translate_property(
    obj: QtCore.QObject,
    property_name: str,
    getter: Any,
    setter: Any,
) -> None:
    try:
        current = getter()
    except (RuntimeError, TypeError):
        return
    if not isinstance(current, str) or not current:
        return
    source = _remember_source(obj, property_name, current)
    translated = str(tr(source))
    if current != translated:
        setter(translated)


def _translate_combo(combo: QtWidgets.QComboBox) -> None:
    blocked = combo.blockSignals(True)
    try:
        for index in range(combo.count()):
            source = combo.itemData(index, SOURCE_TEXT_ROLE)
            if not isinstance(source, str):
                source = _source_text(combo.itemText(index))
                combo.setItemData(index, source, SOURCE_TEXT_ROLE)
            if combo.itemData(index, QtCore.Qt.ItemDataRole.UserRole) is None:
                combo.setItemData(index, source, QtCore.Qt.ItemDataRole.UserRole)
            combo.setItemText(index, str(tr(source)))
    finally:
        combo.blockSignals(blocked)


def translate_object(obj: QtCore.QObject) -> None:
    """Translate supported properties while retaining their English source text."""
    if isinstance(obj, QtWidgets.QComboBox):
        _translate_combo(obj)

    if isinstance(obj, QtWidgets.QTabWidget):
        for index in range(obj.count()):
            key = f"_i18n_source_tab_{index}"
            source = obj.property(key)
            current = obj.tabText(index)
            if not isinstance(source, str) or (not source and current):
                source = _source_text(current)
                obj.setProperty(key, source)
            if source:
                obj.setTabText(index, str(tr(source)))

    if isinstance(obj, QtWidgets.QGroupBox):
        _translate_property(obj, "title", obj.title, obj.setTitle)
    if isinstance(obj, QtWidgets.QMenu):
        _translate_property(obj, "title", obj.title, obj.setTitle)
    if isinstance(obj, QtWidgets.QDockWidget):
        _translate_property(
            obj, "window_title", obj.windowTitle, obj.setWindowTitle
        )
    elif isinstance(obj, QtWidgets.QWidget) and obj.isWindow():
        _translate_property(
            obj, "window_title", obj.windowTitle, obj.setWindowTitle
        )

    if isinstance(obj, QtGui.QAction):
        _translate_property(obj, "text", obj.text, obj.setText)
        _translate_property(obj, "tooltip", obj.toolTip, obj.setToolTip)
        _translate_property(obj, "status_tip", obj.statusTip, obj.setStatusTip)
    elif isinstance(obj, QtWidgets.QAbstractButton):
        _translate_property(obj, "text", obj.text, obj.setText)
    elif isinstance(obj, QtWidgets.QLabel):
        _translate_property(obj, "text", obj.text, obj.setText)

    if isinstance(obj, QtWidgets.QLineEdit):
        _translate_property(
            obj,
            "placeholder",
            obj.placeholderText,
            obj.setPlaceholderText,
        )
    if isinstance(obj, QtWidgets.QProgressDialog):
        _translate_property(obj, "label_text", obj.labelText, obj.setLabelText)

    if isinstance(obj, QtWidgets.QWidget):
        _translate_property(obj, "tooltip", obj.toolTip, obj.setToolTip)
        _translate_property(obj, "status_tip", obj.statusTip, obj.setStatusTip)


def translate_object_tree(root: QtCore.QObject) -> None:
    translate_object(root)
    for child in root.findChildren(QtCore.QObject):
        translate_object(child)


class UiLocalizer(QtCore.QObject):
    """Translates dynamically-created menus and dialogs just before display."""

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() in (
            QtCore.QEvent.Type.Show,
            QtCore.QEvent.Type.ShowToParent,
        ):
            translate_object_tree(watched)
        elif event.type() in (
            QtCore.QEvent.Type.Paint,
            QtCore.QEvent.Type.ToolTipChange,
            QtCore.QEvent.Type.WindowTitleChange,
            QtCore.QEvent.Type.ActionChanged,
        ) and isinstance(
            watched,
            (
                QtWidgets.QLabel,
                QtWidgets.QAbstractButton,
                QtWidgets.QProgressDialog,
                QtGui.QAction,
            ),
        ):
            translate_object(watched)
        return False


def install(app: QtWidgets.QApplication) -> None:
    """Install translation support. Must be called before creating UI widgets."""
    global _language, _localizer
    _language = load_language()
    _load_translations()
    _localizer = UiLocalizer(app)
    app.installEventFilter(_localizer)
