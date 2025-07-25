from omnipy.shared.enums.data import BackoffStrategy

DEFAULT_RETRIES = 5
DEFAULT_BACKOFF_STRATEGY = BackoffStrategy.EXPONENTIAL
DEFAULT_RETRY_STATUSES = (408, 425, 429, 500, 502, 503, 504)
