import logging
import time

from cerebras.cloud.sdk import Cerebras

# Default model to use across all functions
DEFAULT_MODEL = "qwen-3-235b-a22b-instruct-2507"

logger = logging.getLogger(__name__)

# Maximum number of retry attempts for transient / rate-limit errors
_MAX_RETRIES = 3
# Base delay (seconds) for exponential back-off
_BASE_DELAY = 2.0


class TokenQuotaExceededError(Exception):
    """Raised when the Cerebras API returns a daily token-quota error (HTTP 429)."""


class CerebrasClient:
    def __init__(self, api_key):
        # This client now strictly requires an api_key to be passed by the caller.
        # The caller (cerebras_chat_main.py) is responsible for sourcing this key.
        if not api_key:
            # This should ideally be caught before calling, but as a safeguard.
            raise ValueError("CerebrasClient must be initialized with an API key.")

        # Directly use the provided api_key for Cerebras SDK initialization.
        self.client = Cerebras(api_key=api_key)

    # ------------------------------------------------------------------
    # Internal helper – retry with exponential back-off on 429 errors
    # ------------------------------------------------------------------
    @staticmethod
    def _is_quota_error(exc):
        """Return True if *exc* signals a daily token-quota limit."""
        msg = str(exc).lower()
        return "429" in msg and (
            "token" in msg or "quota" in msg or "too_many_tokens" in msg
        )

    def _call_with_retry(self, fn, *args, **kwargs):
        """Call *fn* with retry logic for transient 429 errors.

        If the error indicates the **daily** token quota has been exhausted
        (as opposed to a short-lived rate-limit burst), we surface a clear
        ``TokenQuotaExceededError`` immediately so the caller can show a
        friendly message instead of silently retrying.
        """
        last_exc = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                last_exc = exc
                if self._is_quota_error(exc):
                    # Daily quota – retrying won't help
                    raise TokenQuotaExceededError(str(exc)) from exc
                # For other transient errors, back off and retry
                if attempt < _MAX_RETRIES:
                    delay = _BASE_DELAY * (2 ** (attempt - 1))
                    logger.warning(
                        "Cerebras API call failed (attempt %d/%d), "
                        "retrying in %.1fs: %s",
                        attempt,
                        _MAX_RETRIES,
                        delay,
                        exc,
                    )
                    time.sleep(delay)
        # All retries exhausted
        raise last_exc  # type: ignore[misc]

    def get_chat_completion(self, messages, model=DEFAULT_MODEL, **kwargs):
        # messages is expected to be a list of message dicts, e.g.:
        # [{"role": "system", "content": "You are helpful"},
        #  {"role": "user", "content": "Hello!"}]
        # **kwargs will capture any other parameters like max_completion_tokens, temperature, etc.

        return self._call_with_retry(
            self.client.chat.completions.create,
            messages=messages,
            model=model,
            **kwargs,
        )

    # Text completion can be kept if desired, but chat is the focus
    def get_text_completion(self, user_message, model=DEFAULT_MODEL):
        return self._call_with_retry(
            self.client.completions.create,
            prompt=user_message,
            model=model,
            max_completion_tokens=20480,
            top_p=1,
        )
