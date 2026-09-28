"""Small strict input checks shared verbatim by the draft public programs."""
import math


def fields(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError("unexpected fields")
    return value


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("invalid integer")
    return value


def finite(value):
    if type(value) not in (int, float):
        raise ValueError("invalid number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError("number outside float range") from exc
    if not math.isfinite(result):
        raise ValueError("nonfinite number")
    return result


def names(value):
    if (not isinstance(value, list) or any(not isinstance(v, str) or not v for v in value)
            or len(set(value)) != len(value)):
        raise ValueError("distinct names required")
    return list(value)


def vector(value, size):
    if not isinstance(value, list) or len(value) != size:
        raise ValueError("wrong vector size")
    return [finite(v) for v in value]


def bits(value, size):
    if not isinstance(value, list) or len(value) != size or any(type(v) is not bool for v in value):
        raise ValueError("boolean vector required")
    return list(value)
