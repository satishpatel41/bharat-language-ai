from pydantic import BaseModel, Field, field_validator


class TranslateTextRequest(BaseModel):
    text: str = Field(max_length=10_000)
    target_language: str
    source_language: str = "auto"

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be blank")
        return value


class LanguageOut(BaseModel):
    code: str
    name: str
    native_name: str
    script: str
    speech_input: bool


class TranslationResult(BaseModel):
    source_language: str
    target_language: str
    original_text: str
    translated_text: str


class ImageTranslationResult(BaseModel):
    source_language: str
    target_language: str
    extracted_text: str
    translated_text: str


class SegmentOut(BaseModel):
    start: float
    end: float
    text: str
    translated_text: str


class MediaTranslationResult(BaseModel):
    source_language: str
    target_language: str
    transcript: str
    translated_text: str
    segments: list[SegmentOut]
    srt: str
