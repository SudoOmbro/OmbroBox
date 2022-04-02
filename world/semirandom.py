import random
from time import time

_NUMBERS = [*range(1024)]
random.shuffle(_NUMBERS)
_NUMBERS = tuple(_NUMBERS)

_LAST_PLACE = len(_NUMBERS) - 1
_CURSOR: int = -1


def rand(max_num: int) -> int:
    """
    Implements the DOOM way of getting random numbers, faster than the base random by about 3.5 times.

    :return: a random integer between 0 and max_num
    """
    global _CURSOR
    if _CURSOR == _LAST_PLACE:
        _CURSOR = 0
    else:
        _CURSOR += 1
    return _NUMBERS[_CURSOR] % max_num


if __name__ == "__main__":
    start_time = time()
    for _ in range(1000000):
        random.randint(0, 10)
    random_time = time() - start_time
    start_time = time()
    for _ in range(1000000):
        rand(10)
    semirandom_time = time() - start_time
    print(f"Random time: {random_time}")
    print(f"Semi-Random time: {semirandom_time}")
