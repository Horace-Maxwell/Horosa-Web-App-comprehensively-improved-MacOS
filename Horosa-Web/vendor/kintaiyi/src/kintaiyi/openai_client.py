import logging
import time

from openai import OpenAI

# Default model to use across all functions
DEFAULT_MODEL = "gpt-4o-mini"

logger = logging.getLogger(__name__)

# Maximum number of retry attempts for transient / rate-limit errors
_MAX_RETRIES = 3
# Base delay (seconds) for exponential back-off
_BASE_DELAY = 2.0


class TokenQuotaExceededError(Exception):
    """Raised when the OpenAI API returns a quota/rate-limit error (HTTP 429)."""


class OpenAIClient:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("OpenAIClient must be initialized with an API key.")
        self.client = OpenAI(api_key=api_key)

    # ------------------------------------------------------------------
    # Internal helper – retry with exponential back-off on 429 errors
    # ------------------------------------------------------------------
    @staticmethod
    def _is_quota_error(exc):
        """Return True if *exc* signals a quota/rate-limit error."""
        msg = str(exc).lower()
        return "429" in msg or "rate_limit" in msg or "quota" in msg or "insufficient_quota" in msg

    def _call_with_retry(self, fn, *args, **kwargs):
        """Call *fn* with retry logic for transient 429 errors."""
        last_exc = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                last_exc = exc
                if self._is_quota_error(exc):
                    raise TokenQuotaExceededError(str(exc)) from exc
                if attempt < _MAX_RETRIES:
                    delay = _BASE_DELAY * (2 ** (attempt - 1))
                    logger.warning(
                        "OpenAI API call failed (attempt %d/%d), "
                        "retrying in %.1fs: %s",
                        attempt,
                        _MAX_RETRIES,
                        delay,
                        exc,
                    )
                    time.sleep(delay)
        raise last_exc  # type: ignore[misc]

    def get_chat_completion(self, messages, model=DEFAULT_MODEL, **kwargs):
        return self._call_with_retry(
            self.client.chat.completions.create,
            messages=messages,
            model=model,
            **kwargs,
        )
