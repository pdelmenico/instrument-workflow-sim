"""Timing distribution sampling functions for operation durations.

This module provides functions to sample operation durations from various
probability distributions. All functions use NumPy's random number generator
for consistency and reproducibility via random seeds.
"""
import numpy as np
from typing import Dict, Any


def sample_fixed(value: float) -> float:
    """Sample from fixed timing distribution (deterministic).

    Args:
        value: The fixed duration value in seconds

    Returns:
        The fixed value

    Raises:
        ValueError: If value is negative

    Example:
        >>> duration = sample_fixed(10.0)
        >>> assert duration == 10.0
    """
    if value < 0:
        raise ValueError(f"Fixed timing value must be non-negative, got {value}")
    return float(value)


def sample_triangular(min_val: float, mode: float, max_val: float) -> float:
    """Sample from triangular distribution.

    The triangular distribution is commonly used when engineers estimate
    optimistic (min), most likely (mode), and pessimistic (max) durations.

    Args:
        min_val: Minimum possible duration (optimistic)
        mode: Most likely duration (peak of distribution)
        max_val: Maximum possible duration (pessimistic)

    Returns:
        Sampled duration in seconds

    Raises:
        ValueError: If parameters don't satisfy min_val <= mode <= max_val
        ValueError: If any parameter is negative

    Example:
        >>> np.random.seed(42)
        >>> duration = sample_triangular(8.0, 10.0, 12.0)
        >>> assert 8.0 <= duration <= 12.0
    """
    if min_val < 0:
        raise ValueError(f"Triangular min must be non-negative, got {min_val}")
    if mode < 0:
        raise ValueError(f"Triangular mode must be non-negative, got {mode}")
    if max_val < 0:
        raise ValueError(f"Triangular max must be non-negative, got {max_val}")

    if not (min_val <= mode <= max_val):
        raise ValueError(
            f"Triangular parameters must satisfy min <= mode <= max, "
            f"got min={min_val}, mode={mode}, max={max_val}"
        )

    # Handle edge case where all values are equal
    if min_val == max_val:
        return float(min_val)

    return float(np.random.triangular(min_val, mode, max_val))


def sample_exponential(mean: float) -> float:
    """Sample from exponential distribution.

    The exponential distribution is commonly used for modeling process times
    with high variability, particularly for chemical reactions or biological
    processes where completion time is stochastic.

    Args:
        mean: Mean (expected value) of the distribution in seconds

    Returns:
        Sampled duration in seconds

    Raises:
        ValueError: If mean is not positive

    Example:
        >>> np.random.seed(42)
        >>> duration = sample_exponential(100.0)
        >>> assert duration > 0
    """
    if mean <= 0:
        raise ValueError(f"Exponential mean must be positive, got {mean}")

    return float(np.random.exponential(mean))


def sample_timing(timing_model: Dict[str, Any]) -> float:
    """Sample operation duration from timing model specification.

    This is the main entry point for sampling timing distributions.
    It dispatches to the appropriate sampling function based on the
    timing model type.

    Args:
        timing_model: Dictionary with 'type' and distribution parameters
            Examples:
            - {"type": "fixed", "value": 10.0}
            - {"type": "triangular", "min": 5.0, "mode": 10.0, "max": 15.0}
            - {"type": "exponential", "mean": 30.0}

    Returns:
        Sampled duration in seconds

    Raises:
        ValueError: If timing type is unsupported
        ValueError: If required parameters are missing
        ValueError: If parameters are invalid

    Example:
        >>> timing = {"type": "fixed", "value": 10.0}
        >>> duration = sample_timing(timing)
        >>> assert duration == 10.0
    """
    if not isinstance(timing_model, dict):
        raise ValueError(f"timing_model must be a dictionary, got {type(timing_model)}")

    if "type" not in timing_model:
        raise ValueError("timing_model must have 'type' field")

    timing_type = timing_model["type"]

    if timing_type == "fixed":
        if "value" not in timing_model:
            raise ValueError("Fixed timing model requires 'value' parameter")
        return sample_fixed(timing_model["value"])

    elif timing_type == "triangular":
        required = ["min", "mode", "max"]
        missing = [p for p in required if p not in timing_model]
        if missing:
            raise ValueError(f"Triangular timing model missing parameters: {missing}")
        return sample_triangular(
            timing_model["min"],
            timing_model["mode"],
            timing_model["max"]
        )

    elif timing_type == "exponential":
        if "mean" not in timing_model:
            raise ValueError("Exponential timing model requires 'mean' parameter")
        return sample_exponential(timing_model["mean"])

    else:
        raise ValueError(
            f"Unsupported timing type '{timing_type}'. "
            f"Supported types: fixed, triangular, exponential"
        )


def set_random_seed(seed: int) -> None:
    """Set the random seed for reproducible simulations.

    Args:
        seed: Random seed value

    Example:
        >>> set_random_seed(42)
        >>> d1 = sample_exponential(100.0)
        >>> set_random_seed(42)
        >>> d2 = sample_exponential(100.0)
        >>> assert d1 == d2
    """
    np.random.seed(seed)
