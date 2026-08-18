from collections.abc import Iterable
from typing import cast


def flatten_queue[T](*queue: T | Iterable[T]) -> list[T]:
    """Flatten the queue to allow nested lists to be put inside of it"""
    # *args creates a tuple, and the queue is consumed from the front and
    # pushed onto again, so work on a list copy under its own name
    remaining: list[T | Iterable[T]] = list(queue)

    flattened: list[T] = []

    while remaining:
        el = remaining.pop(0)

        # This entry is an iterable too, unpack it
        # & add to front of the queue
        # str and bytes are Iterable as well, but a teacher who passes one here meant it as
        # a single (wrong) value. Exploding it into characters buries that mistake under a
        # pile of nonsense entries, so keep them whole and let them fail as non-Checks
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            # Cast to a list first (allows map, generators, ...)
            nested = list(el)

            # Iterate in reverse to keep the order of checks!
            for nested_el in reversed(nested):
                remaining.insert(0, nested_el)
        else:
            # T could itself be str, so as far as the annotation goes a str landing here
            # is still an Iterable[T]. It never is one in practice
            flattened.append(cast("T", el))

    return flattened
