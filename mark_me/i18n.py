"""
Mark.me - Internationalization (i18n). Default language: English.
"""
import json
import os

_DEFAULT_LANG = "en"
_TRANSLATIONS: dict[str, dict[str, str]] = {}
_CURRENT_LANG = _DEFAULT_LANG

_LOCALES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")


def _load(lang: str) -> dict[str, str]:
    path = os.path.join(_LOCALES_DIR, f"{lang}.json")
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def set_lang(lang: str) -> None:
    """Set current language (e.g. 'en', 'pt_BR', 'de', 'es')."""
    global _CURRENT_LANG, _TRANSLATIONS
    _CURRENT_LANG = lang or _DEFAULT_LANG
    _TRANSLATIONS[_CURRENT_LANG] = _load(_CURRENT_LANG)
    if not _TRANSLATIONS[_CURRENT_LANG] and _CURRENT_LANG != _DEFAULT_LANG:
        _TRANSLATIONS[_CURRENT_LANG] = _load(_DEFAULT_LANG)


def get_lang() -> str:
    """Return current language code."""
    return _CURRENT_LANG


def t(key: str, **kwargs: str | int) -> str:
    """Return translated string for key. Use t('key', n=32) for placeholders like {n}."""
    if _CURRENT_LANG not in _TRANSLATIONS:
        set_lang(_CURRENT_LANG)
    msg = _TRANSLATIONS.get(_CURRENT_LANG, {}).get(key)
    if msg is None:
        msg = _load(_DEFAULT_LANG).get(key, key)
    if kwargs:
        try:
            return msg.format(**kwargs)
        except (KeyError, ValueError):
            return msg
    return msg


# Load default on import
set_lang(_DEFAULT_LANG)
