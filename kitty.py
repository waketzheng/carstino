import functools
import inspect
import time
from contextlib import asynccontextmanager, contextmanager
from typing import Callable, Coroutine

try:
    import anyio

    print("Using anyio")

    sleep = anyio.sleep

    def run_async(coro):
        async def runner(coro):
            return await coro

        return anyio.run(runner, coro)

    async def gather(*coros):
        results = [None] * len(coros)

        async def runner(coro, i):
            results[i] = await coro

        async with anyio.create_task_group() as tg:
            for i, coro in enumerate(coros):
                tg.start_soon(runner, coro, i)

        return results

    def be_afunc(coro: Coroutine) -> Callable:
        async def do_await():
            return await coro

        return do_await

    @asynccontextmanager
    async def start_tasks(coro, *more):
        async with anyio.create_task_group() as tg:
            with anyio.CancelScope(shield=True):
                tg.start_soon(be_afunc(coro))
                for c in more:
                    tg.start_soon(be_afunc(c))
                yield
                tg.cancel_scope.cancel()

except ImportError:
    import asyncio

    sleep = asyncio.sleep
    run_async = asyncio.run
    gather = asyncio.gather

    @asynccontextmanager
    async def start_tasks(coro, *more):
        tasks = [asyncio.create_task(i) for i in (coro, *more)]
        yield
        for t in tasks:
            t.cancel()


@contextmanager
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
        cost = end - start
        if decimal_places is not None:
            cost = round(cost, decimal_places)
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

        >>> res = timeit(sync_func)(*args, **kwargs)
        >>> result = await timeit(async_func)(*args, **kwargs)
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

    async def test_start_tasks():
        async with start_tasks(async_func(), do_sth()):
            print(555, "tasks started.")

    run_async(test_start_tasks())


if __name__ == "__main__":
    _test()
