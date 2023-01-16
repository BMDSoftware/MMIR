#from main.algorithm import algorithmCore
from algorithms.algorithm import algorithmCore
from typing import Any, Callable



algorithm_creation_func = {}



def register(algorithm_name, creation_func ):
    algorithm_creation_func[algorithm_name] = creation_func


def unregister(algorithm_name) -> None:
    algorithm_creation_func.pop(algorithm_name, None)


def create(algorithm_name, fixIm, movIm):
    try:
        creator_func = algorithm_creation_func[algorithm_name]
    except KeyError:
        raise ValueError(f"unknown algorithm name {algorithm_name!r}") from None
    return creator_func(fixIm, movIm )

def getAlgNames():
    return algorithm_creation_func.keys()