import pytest

from app.errors import UnsupportedLanguageError
from app.languages import LANGUAGES, get_language, is_supported, resolve_source

SCHEDULED_LANGUAGES = {
    "as", "bn", "brx", "doi", "gu", "hi", "kn", "ks", "kok", "mai", "ml",
    "mni", "mr", "ne", "or", "pa", "sa", "sat", "sd", "ta", "te", "ur",
}  # fmt: skip


def test_all_22_scheduled_languages_are_supported():
    codes = {lang.code for lang in LANGUAGES}
    assert codes >= SCHEDULED_LANGUAGES
    assert "en" in codes


def test_language_codes_are_unique():
    codes = [lang.code for lang in LANGUAGES]
    assert len(codes) == len(set(codes))


def test_get_language_is_case_and_whitespace_insensitive():
    assert get_language(" HI ").name == "Hindi"


def test_get_language_rejects_unknown_code():
    with pytest.raises(UnsupportedLanguageError):
        get_language("xx")


def test_is_supported():
    assert is_supported("ta")
    assert not is_supported("fr")


@pytest.mark.parametrize("value", [None, "auto", "AUTO"])
def test_resolve_source_auto(value):
    assert resolve_source(value) is None


def test_resolve_source_validates_explicit_code():
    assert resolve_source("GU") == "gu"
    with pytest.raises(UnsupportedLanguageError):
        resolve_source("zz")
