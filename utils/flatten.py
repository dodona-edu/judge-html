from collections.abc import Iterable


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
        if isinstance(el, Iterable):
            # Cast to a list first (allows map, generators, ...)
            nested = list(el)

            # Iterate in reverse to keep the order of checks!
            for nested_el in reversed(nested):
                remaining.insert(0, nested_el)
        else:
            flattened.append(el)

    return flattened
