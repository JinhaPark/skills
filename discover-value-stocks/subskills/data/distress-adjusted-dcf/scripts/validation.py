"""Shared validation for finite real-valued model inputs and arithmetic."""
from collections.abc import Sequence
from math import isfinite
from numbers import Real


def finite_number(value, name):
    """Reject implicit conversions (including bool) and non-finite numbers."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f'{name} must be a real number (not bool)')
    try:
        valid = isfinite(value)
    except OverflowError as exc:
        raise ValueError(f'{name} is outside the supported numeric range') from exc
    if not valid:
        raise ValueError(f'{name} must be finite')
    return value


def finite_series(values, name):
    """Snapshot a sequence and validate every element before calculating."""
    if isinstance(values, (str, bytes, bytearray)) or not isinstance(values, Sequence):
        raise TypeError(f'{name} must be a sequence of real numbers')
    return [finite_number(value, f'{name}[{i}]') for i, value in enumerate(values)]
