import threading
import multiprocessing as mp


def in_pool(async: bool=False, ):
    """
    Returns a decorator that modifies a method to run in pool.
    :param async: boolean indicating whether or not result should be
    waited for.
    :return: decorator callable
    """

    def decorator(func):
        """
        Decorator that modifies method so that it is run in a separate worker
        thread.
        :arg func: callable
        :return: callable func
        """

        def wrapper(*args, **kwargs):

            def parallel_func():
                if not getattr(_thread_local, 'initialized', False):
                    # initialize thread

                    setattr(_thread_local, 'initialized', True)

                func(*args, **kwargs)

            pool = _get_pool()
            assert isinstance(pool, mp.Pool)
            if async:
                pool.apply_async(parallel_func)
            else:
                result = _get_pool().apply_async(parallel_func)
                return result.get()

        wrapper.__name__ = func.__name__  # rename wrapper to wrapped func

        return wrapper

    return decorator


def _get_pool():
    global _worker_pool
    if _worker_pool is None:
        _worker_pool = mp.Pool(mp.cpu_count())
    return _worker_pool


_worker_pool = None

_thread_local = threading.local()
