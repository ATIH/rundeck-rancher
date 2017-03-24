"""
q
"""
# http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/

from functools import wraps
import time
import sys

# hiding traceback
# sys.tracebacklimit = 0

_default_retry_interval = 10  # seconds
_default_retry_attempts = 10


def log(message):
    """
    q
    """
    print message
    sys.stdout.flush()


def retry(interval=_default_retry_interval, attempts=_default_retry_attempts):
    """
    q
    """
    def deco_retry(func):
        """
        q
        """
        @wraps(func)
        def retry_wrapper(*args, **kwargs):
            """
            q
            """
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                #pylint: disable=w0703
                except Exception as e:
                    attempt += 1
                    if attempt > attempts and attempts >= 0:
                        raise e
                    log("[ E ] {}".format(e))
                    if attempts >= 0:
                        log("[ I ] Retrying attempt {}/{} in {} seconds...".format(attempt, attempts, interval))
                    else:
                        log("[ I ] Retrying attempt {} in {} seconds...".format(attempt, interval))
                    time.sleep(interval)
        return retry_wrapper
    return deco_retry
