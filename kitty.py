import contextlib
import functools
import inspect
import time

try:
    import anyio

    print("Using anyio")

    sleep = anyio.sleep

    def run_async(coro):
        async def runner(coro):
            return await coro

        return anyio.run(runner, coro)

except ImportError:
    import asyncio

    run_async = asyncio.run
    sleep = asyncio.sleep


@contextlib.contextmanager
def timer(message: str, decimal_places=1):
    """Print time cost of the function.

    Usage::
        >>> @timer("Message")
        >>> async def main():
        ...     # ... async code ...

        >>> @timer('sync function')
        >>> def read_text(filename):
        ...     return Path(filename).read_text()

        >>> with timer('do sth ...'):
        ...     # ... async code or sync code ...
    """
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        cost = round(end - start, decimal_places)
        print(message, "Cost:", cost, "seconds")


def timeit(func):
    """Print time cost of the function.

    Usage::
        >>> @timeit
        >>> async def main():
        ...     # ... async code ...

        >>> @timeit
        >>> def read_text(filename):
        ...     return Path(filename).read_text()

        >>> text = timeit(async_or_sync_func)(*args, **kwargs)
    """

    func_name = getattr(func, "__name__", str(func))
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def deco(*args, **kwargs):
            with timer(func_name):
                return await func(*args, **kwargs)

    else:

        @functools.wraps(func)
        def deco(*args, **kwargs):
            with timer(func_name):
                return func(*args, **kwargs)

    return deco


def _test():
    from datetime import datetime

    @timeit
    async def do_sth():
        print(111, datetime.now())
        await sleep(0.5)
        return datetime.now()

    print(run_async(do_sth()))
    print("-------------------")

    @timeit
    def foo(*args, **kwargs):
        print(222, datetime.now())
        time.sleep(0.3)
        return args, kwargs, datetime.now()

    print(foo(1, a=2))
    print("-------------------")

    @timer("Wonderful")
    async def async_func():
        print(333, datetime.now())
        await sleep(0.2)
        return datetime.now()

    print(run_async(async_func()))
    print("-------------------")

    @timer("Beautiful")
    def func():
        print(444, datetime.now())
        time.sleep(0.1)
        return datetime.now()

    print(func())
    print("-------------------")


if __name__ == "__main__":
    _test()
