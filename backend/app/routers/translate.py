from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.config import Settings, get_settings
from app.deps import get_stt, get_translator
from app.languages import LANGUAGES
from app.providers.base import SpeechToText, Translator
from app.schemas import (
    ImageTranslationResult,
    LanguageOut,
    MediaTranslationResult,
    TranslateTextRequest,
    TranslationResult,
)
from app.services import image as image_service
from app.services import media as media_service
from app.services import text as text_service
from app.uploads import AUDIO_SUFFIXES, VIDEO_SUFFIXES, read_limited, spooled_upload

router = APIRouter(prefix="/api")

TranslatorDep = Annotated[Translator, Depends(get_translator)]
SttDep = Annotated[SpeechToText, Depends(get_stt)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


@router.get("/languages", response_model=list[LanguageOut])
async def list_languages() -> list[LanguageOut]:
    return [
        LanguageOut(
            code=lang.code,
            name=lang.name,
            native_name=lang.native_name,
            script=lang.script,
            speech_input=lang.whisper_code is not None,
        )
        for lang in LANGUAGES
    ]


@router.post("/translate/text", response_model=TranslationResult)
async def translate_text(
    body: TranslateTextRequest, translator: TranslatorDep
) -> TranslationResult:
    return await text_service.translate_text(
        translator, body.text, body.target_language, body.source_language
    )


@router.post("/translate/image", response_model=ImageTranslationResult)
async def translate_image(
    translator: TranslatorDep,
    settings: SettingsDep,
    file: Annotated[UploadFile, File()],
    target_language: Annotated[str, Form()],
) -> ImageTranslationResult:
    data = await read_limited(file, settings.max_image_bytes)
    return await image_service.translate_image(translator, data, target_language)


@router.post("/translate/audio", response_model=MediaTranslationResult)
async def translate_audio(
    translator: TranslatorDep,
    stt: SttDep,
    settings: SettingsDep,
    file: Annotated[UploadFile, File()],
    target_language: Annotated[str, Form()],
    source_language: Annotated[str, Form()] = "auto",
) -> MediaTranslationResult:
    async with spooled_upload(file, settings.max_audio_bytes, AUDIO_SUFFIXES) as path:
        return await media_service.translate_audio(
            stt, translator, path, target_language, source_language
        )


@router.post("/translate/video", response_model=MediaTranslationResult)
async def translate_video(
    translator: TranslatorDep,
    stt: SttDep,
    settings: SettingsDep,
    file: Annotated[UploadFile, File()],
    target_language: Annotated[str, Form()],
    source_language: Annotated[str, Form()] = "auto",
) -> MediaTranslationResult:
    async with spooled_upload(file, settings.max_video_bytes, VIDEO_SUFFIXES) as path:
        return await media_service.translate_video(
            stt,
            translator,
            path,
            target_language,
            source_language,
            ffmpeg_timeout=settings.ffmpeg_timeout_seconds,
        )
