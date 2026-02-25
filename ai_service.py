import time
import os
from typing import Optional
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError, APIStatusError
import structlog

logger = structlog.get_logger()

def generate_summary(content: str, user_id: Optional[int] = None) -> Optional[str]:
    """
    Generate a concise 1-2 sentence summary using OpenAI API.
    Returns None on any failure — never raises.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        logger.warning("ai_summary_skipped", reason="OPENAI_API_KEY not set", user_id=user_id)
        return None

    logger.info("ai_summary_generation_attempt", content_length=len(content), user_id=user_id)

    for attempt in range(2):
        start_time = time.time()
        try:
            client = OpenAI(api_key=api_key, timeout=5.0)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize this note in 1-2 concise sentences: {content}"
                    }
                ],
                max_tokens=100,
            )
            summary = response.choices[0].message.content.strip()
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info("ai_summary_generation_success",
                       content_length=len(content),
                       summary_length=len(summary),
                       latency_ms=latency_ms,
                       user_id=user_id)
            return summary

        except APITimeoutError as e:
            logger.error("ai_summary_generation_failure", error_type="timeout", error_message=str(e), attempt=attempt + 1)
        except RateLimitError as e:
            logger.error("ai_summary_generation_failure", error_type="rate_limit", error_message=str(e), attempt=attempt + 1)
        except APIConnectionError as e:
            logger.error("ai_summary_generation_failure", error_type="connection_error", error_message=str(e), attempt=attempt + 1)
        except APIStatusError as e:
            logger.error("ai_summary_generation_failure", error_type="api_status_error", error_message=str(e), attempt=attempt + 1)
        except Exception as e:
            logger.error("ai_summary_generation_failure", error_type="unexpected", error_message=str(e), attempt=attempt + 1)
            break

    return None
