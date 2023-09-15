import functools
import inspect
import time
from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    asynccontextmanager,
    contextmanager,
)
from typing import Any, Callable, Union

try:
    from anyio import sleep
    from asyncur import gather, run_async, start_tasks

    print("Using anyio")
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


class Timer(AbstractContextManager, AbstractAsyncContextManager):
    """Print time cost of the function.

    Usage::
        >>> @Timer
        >>> async def main():
        ...     # ... async code or sync code ...

        >>> @Timer
        >>> def read_text(filename):
        ...     return Path(filename).read_text()

        >>> with Timer('do sth ...'):
        ...     # ... sync code ...

        >>> async with Timer('do sth ...'):
        ...     # ... async code ...
    """

    def __init__(self, message: Union[str, Callable], decimal_places=1):
        func = None
        if callable(message):  # Use as decorator
            func = message
            if hasattr(func, "__name__"):
                self.__name__ = message = func.__name__
            else:
                message = str(func)
        self.message = message
        self.func = func
        self.decimal_places = decimal_places
        self.end = self.start = time.time()

    def _echo(self):
        self.end = self.echo_cost(self.start, self.decimal_places, self.message)

    @staticmethod
    def echo_cost(start: float, decimal_places: int, message: str) -> float:
        end = time.time()
        cost = end - start
        if decimal_places is not None:
            cost = round(cost, decimal_places)
        print(message, "Cost:", cost, "seconds")
        return end

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, *args, **kwargs):
        self.__exit__(*args, **kwargs)

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args, **kwargs):
        self._echo()

    def _recreate_cm(self):
        return self.__class__(self.func or self.message, self.decimal_places)

    def __call__(self, *args, **kwargs) -> Any:
        if self.func is None:
            return
        if inspect.iscoroutinefunction(self.func):

            @functools.wraps(self.func)
            async def inner(*args, **kwds):
                async with self._recreate_cm():
                    return await self.func(*args, **kwargs)

            return inner(*args, **kwargs)
        else:
            with self._recreate_cm():
                return self.func(*args, **kwargs)


@contextmanager
def timer(message: str, decimal_places=1):
    """Print time cost of the function.

    Usage::
        >>> @timer('message')
        >>> def read_text(filename):
        ...     return Path(filename).read_text()

        >>> with timer('do sth ...'):
        ...     # ... sync code ...
    """
    start = time.time()
    try:
        yield
    finally:
        Timer.echo_cost(start, decimal_places, message)


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
            async with Timer(func_name):
                return await func(*args, **kwargs)

    else:

        @functools.wraps(func)
        def deco(*args, **kwargs):
            with Timer(func_name):
                return func(*args, **kwargs)

    return deco


def _test():
    from datetime import datetime

    @timeit
    async def do_sth(seconds):
        print(111, datetime.now())
        await sleep(seconds)
        return datetime.now()

    now = datetime.now()
    print(f"Start at: {now}")
    seconds = 0.1
    later = run_async(do_sth(seconds))
    delta = later - now
    assert delta.seconds == 0, "sleep too long"
    assert round(delta.microseconds / 10**6, 1) == seconds
    print(later, "await sleep and return as expected.")
    print("-------------------")

    @timeit
    def foo(*args, **kwargs):
        print(222, datetime.now())
        time.sleep(args[0])
        return args, kwargs, datetime.now()

    seconds = 0.2
    now = datetime.now()
    foo(seconds, 1, a=2)
    later = datetime.now()
    delta = later - now
    assert delta.seconds == 0, "sleep too long"
    assert round(delta.microseconds / 10**6, 1) == seconds
    print(later, "block sleep with {seconds=}")
    print("-------------------")

    @Timer
    async def async_func(seconds):
        print(333, datetime.now())
        await sleep(seconds)
        return datetime.now()

    seconds = 0.3
    now = datetime.now()
    later = run_async(async_func(seconds))
    delta = later - now
    assert delta.seconds == 0, "sleep too long"
    assert round(delta.microseconds / 10**6, 1) == seconds
    print(later, "Decorater for async func worked.")
    print("-------------------")

    @timer("Beautiful")
    def func(seconds):
        print(444.1, datetime.now())
        time.sleep(seconds)
        return datetime.now()

    seconds = 0.4
    now = datetime.now()
    later = func(seconds)
    delta = later - now
    assert delta.seconds == 0, "sleep too long"
    assert round(delta.microseconds / 10**6, 1) == seconds

    @Timer
    def func_with_timer_class(seconds):
        print(444.2, datetime.now())
        time.sleep(seconds)
        return datetime.now()

    now = datetime.now()
    later = func_with_timer_class(seconds)
    delta = later - now
    assert delta.seconds == 0, "sleep too long"
    assert round(delta.microseconds / 10**6, 1) == seconds

    print(later, "Decorater for sync func worked.")
    print("-------------------")

    async def test_start_tasks():
        async with start_tasks(async_func(0.2), do_sth(0.5)):
            print(555, "tasks started.")

    run_async(test_start_tasks())


if __name__ == "__main__":
    _test()
