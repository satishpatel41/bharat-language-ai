"""Supported languages: the 22 scheduled languages of India plus English."""

from __future__ import annotations

from dataclasses import dataclass

from app.errors import UnsupportedLanguageError

AUTO = "auto"


@dataclass(frozen=True, slots=True)
class Language:
    code: str
    name: str
    native_name: str
    script: str
    # Code understood by the speech engine. None means the engine has no
    # dedicated support, so audio in this language falls back to auto-detect.
    whisper_code: str | None = None


LANGUAGES: tuple[Language, ...] = (
    Language("as", "Assamese", "অসমীয়া", "Bengali-Assamese", "as"),
    Language("bn", "Bengali", "বাংলা", "Bengali", "bn"),
    Language("brx", "Bodo", "बड़ो", "Devanagari"),
    Language("doi", "Dogri", "डोगरी", "Devanagari"),
    Language("en", "English", "English", "Latin", "en"),
    Language("gu", "Gujarati", "ગુજરાતી", "Gujarati", "gu"),
    Language("hi", "Hindi", "हिन्दी", "Devanagari", "hi"),
    Language("kn", "Kannada", "ಕನ್ನಡ", "Kannada", "kn"),
    Language("ks", "Kashmiri", "کٲشُر", "Perso-Arabic"),
    Language("kok", "Konkani", "कोंकणी", "Devanagari"),
    Language("mai", "Maithili", "मैथिली", "Devanagari"),
    Language("ml", "Malayalam", "മലയാളം", "Malayalam", "ml"),
    Language("mni", "Manipuri (Meitei)", "ꯃꯩꯇꯩꯂꯣꯟ", "Meitei Mayek"),
    Language("mr", "Marathi", "मराठी", "Devanagari", "mr"),
    Language("ne", "Nepali", "नेपाली", "Devanagari", "ne"),
    Language("or", "Odia", "ଓଡ଼ିଆ", "Odia"),
    Language("pa", "Punjabi", "ਪੰਜਾਬੀ", "Gurmukhi", "pa"),
    Language("sa", "Sanskrit", "संस्कृतम्", "Devanagari", "sa"),
    Language("sat", "Santali", "ᱥᱟᱱᱛᱟᱲᱤ", "Ol Chiki"),
    Language("sd", "Sindhi", "سنڌي", "Perso-Arabic", "sd"),
    Language("ta", "Tamil", "தமிழ்", "Tamil", "ta"),
    Language("te", "Telugu", "తెలుగు", "Telugu", "te"),
    Language("ur", "Urdu", "اردو", "Perso-Arabic", "ur"),
)

BY_CODE: dict[str, Language] = {lang.code: lang for lang in LANGUAGES}


def is_supported(code: str) -> bool:
    return code.strip().lower() in BY_CODE


def get_language(code: str) -> Language:
    language = BY_CODE.get(code.strip().lower())
    if language is None:
        raise UnsupportedLanguageError(f"Unsupported language code: {code!r}.")
    return language


def resolve_source(code: str | None) -> str | None:
    """Return a validated source language code, or None when it should be auto-detected."""
    if code is None or code.strip().lower() == AUTO:
        return None
    return get_language(code).code
