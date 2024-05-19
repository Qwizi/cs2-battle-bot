"""Internationalization and localization support."""

import json
from pathlib import Path

from pycord.i18n import I18n, _  # noqa: F401

from .bot import bot

locales = ["en", "pl"]

locales_data = {}

for locale in locales:
    with Path.open(Path("src", "locales", f"{locale}.json")) as f:
        locales_data[locale] = json.load(f)
i18n = I18n(
    bot, consider_user_locale=True, en_US=locales_data["en"], pl=locales_data["pl"]
)
