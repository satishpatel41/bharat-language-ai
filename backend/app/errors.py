"""Application errors. Each carries the HTTP status it should be reported with."""


class AppError(Exception):
    status_code = 500

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UnsupportedLanguageError(AppError):
    status_code = 422


class UnsupportedMediaError(AppError):
    status_code = 415


class PayloadTooLargeError(AppError):
    status_code = 413


class MediaProcessingError(AppError):
    status_code = 422


class TranslationError(AppError):
    status_code = 502


class TranscriptionUnavailableError(AppError):
    status_code = 501


class ConfigurationError(AppError):
    status_code = 503
