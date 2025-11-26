"""Unit tests for timing distribution sampling functions."""
import pytest
import numpy as np
from src.simulation.timing import (
    sample_fixed,
    sample_triangular,
    sample_exponential,
    sample_timing,
    set_random_seed
)


class TestSampleFixed:
    """Tests for fixed timing distribution."""

    def test_sample_fixed_returns_exact_value(self):
        """Test that fixed timing returns exact value."""
        value = 10.5
        result = sample_fixed(value)
        assert result == value

    def test_sample_fixed_zero(self):
        """Test fixed timing with zero value."""
        result = sample_fixed(0.0)
        assert result == 0.0

    def test_sample_fixed_large_value(self):
        """Test fixed timing with large value."""
        result = sample_fixed(10000.0)
        assert result == 10000.0

    def test_sample_fixed_negative_raises_error(self):
        """Test that negative value raises ValueError."""
        with pytest.raises(ValueError, match="Fixed timing value must be non-negative"):
            sample_fixed(-5.0)

    def test_sample_fixed_returns_float(self):
        """Test that return type is float."""
        result = sample_fixed(10)
        assert isinstance(result, float)


class TestSampleTriangular:
    """Tests for triangular distribution sampling."""

    def test_sample_triangular_within_bounds(self):
        """Test that sampled values are within min/max bounds."""
        np.random.seed(42)
        min_val, mode, max_val = 8.0, 10.0, 12.0

        samples = [sample_triangular(min_val, mode, max_val) for _ in range(100)]

        assert all(min_val <= s <= max_val for s in samples)

    def test_sample_triangular_deterministic_with_seed(self):
        """Test that same seed produces same results."""
        np.random.seed(42)
        result1 = sample_triangular(8.0, 10.0, 12.0)

        np.random.seed(42)
        result2 = sample_triangular(8.0, 10.0, 12.0)

        assert result1 == result2

    def test_sample_triangular_edge_case_all_equal(self):
        """Test triangular when min = mode = max."""
        result = sample_triangular(10.0, 10.0, 10.0)
        assert result == 10.0

    def test_sample_triangular_mode_equals_min(self):
        """Test triangular when mode equals min."""
        np.random.seed(42)
        result = sample_triangular(5.0, 5.0, 10.0)
        assert 5.0 <= result <= 10.0

    def test_sample_triangular_mode_equals_max(self):
        """Test triangular when mode equals max."""
        np.random.seed(42)
        result = sample_triangular(5.0, 10.0, 10.0)
        assert 5.0 <= result <= 10.0

    def test_sample_triangular_negative_min_raises_error(self):
        """Test that negative min raises ValueError."""
        with pytest.raises(ValueError, match="Triangular min must be non-negative"):
            sample_triangular(-1.0, 5.0, 10.0)

    def test_sample_triangular_negative_mode_raises_error(self):
        """Test that negative mode raises ValueError."""
        with pytest.raises(ValueError, match="Triangular mode must be non-negative"):
            sample_triangular(0.0, -5.0, 10.0)

    def test_sample_triangular_negative_max_raises_error(self):
        """Test that negative max raises ValueError."""
        with pytest.raises(ValueError, match="Triangular max must be non-negative"):
            sample_triangular(0.0, 5.0, -10.0)

    def test_sample_triangular_mode_less_than_min_raises_error(self):
        """Test that mode < min raises ValueError."""
        with pytest.raises(ValueError, match="must satisfy min <= mode <= max"):
            sample_triangular(10.0, 5.0, 15.0)

    def test_sample_triangular_mode_greater_than_max_raises_error(self):
        """Test that mode > max raises ValueError."""
        with pytest.raises(ValueError, match="must satisfy min <= mode <= max"):
            sample_triangular(5.0, 20.0, 15.0)

    def test_sample_triangular_min_greater_than_max_raises_error(self):
        """Test that min > max raises ValueError."""
        with pytest.raises(ValueError, match="must satisfy min <= mode <= max"):
            sample_triangular(15.0, 10.0, 5.0)

    def test_sample_triangular_returns_float(self):
        """Test that return type is float."""
        result = sample_triangular(5.0, 10.0, 15.0)
        assert isinstance(result, float)


class TestSampleExponential:
    """Tests for exponential distribution sampling."""

    def test_sample_exponential_positive(self):
        """Test that exponential samples are positive."""
        np.random.seed(42)
        samples = [sample_exponential(100.0) for _ in range(100)]
        assert all(s > 0 for s in samples)

    def test_sample_exponential_deterministic_with_seed(self):
        """Test that same seed produces same results."""
        np.random.seed(42)
        result1 = sample_exponential(100.0)

        np.random.seed(42)
        result2 = sample_exponential(100.0)

        assert result1 == result2

    def test_sample_exponential_mean_approximation(self):
        """Test that sample mean approximates specified mean."""
        np.random.seed(42)
        mean = 50.0
        samples = [sample_exponential(mean) for _ in range(10000)]
        sample_mean = np.mean(samples)

        # Sample mean should be close to specified mean (within 5%)
        assert abs(sample_mean - mean) / mean < 0.05

    def test_sample_exponential_zero_mean_raises_error(self):
        """Test that zero mean raises ValueError."""
        with pytest.raises(ValueError, match="Exponential mean must be positive"):
            sample_exponential(0.0)

    def test_sample_exponential_negative_mean_raises_error(self):
        """Test that negative mean raises ValueError."""
        with pytest.raises(ValueError, match="Exponential mean must be positive"):
            sample_exponential(-10.0)

    def test_sample_exponential_small_mean(self):
        """Test exponential with very small mean."""
        np.random.seed(42)
        result = sample_exponential(0.1)
        assert result > 0

    def test_sample_exponential_large_mean(self):
        """Test exponential with very large mean."""
        np.random.seed(42)
        result = sample_exponential(10000.0)
        assert result > 0

    def test_sample_exponential_returns_float(self):
        """Test that return type is float."""
        result = sample_exponential(100.0)
        assert isinstance(result, float)


class TestSampleTiming:
    """Tests for timing model dispatcher."""

    def test_sample_timing_fixed(self):
        """Test dispatching to fixed timing."""
        timing_model = {"type": "fixed", "value": 10.0}
        result = sample_timing(timing_model)
        assert result == 10.0

    def test_sample_timing_triangular(self):
        """Test dispatching to triangular timing."""
        np.random.seed(42)
        timing_model = {"type": "triangular", "min": 8.0, "mode": 10.0, "max": 12.0}
        result = sample_timing(timing_model)
        assert 8.0 <= result <= 12.0

    def test_sample_timing_exponential(self):
        """Test dispatching to exponential timing."""
        np.random.seed(42)
        timing_model = {"type": "exponential", "mean": 100.0}
        result = sample_timing(timing_model)
        assert result > 0

    def test_sample_timing_not_dict_raises_error(self):
        """Test that non-dict timing model raises ValueError."""
        with pytest.raises(ValueError, match="timing_model must be a dictionary"):
            sample_timing("not a dict")

    def test_sample_timing_missing_type_raises_error(self):
        """Test that missing type field raises ValueError."""
        with pytest.raises(ValueError, match="timing_model must have 'type' field"):
            sample_timing({"value": 10.0})

    def test_sample_timing_unsupported_type_raises_error(self):
        """Test that unsupported type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported timing type 'unknown'"):
            sample_timing({"type": "unknown", "value": 10.0})

    def test_sample_timing_fixed_missing_value_raises_error(self):
        """Test that fixed without value raises ValueError."""
        with pytest.raises(ValueError, match="Fixed timing model requires 'value' parameter"):
            sample_timing({"type": "fixed"})

    def test_sample_timing_triangular_missing_min_raises_error(self):
        """Test that triangular without min raises ValueError."""
        with pytest.raises(ValueError, match="Triangular timing model missing parameters"):
            sample_timing({"type": "triangular", "mode": 10.0, "max": 12.0})

    def test_sample_timing_triangular_missing_mode_raises_error(self):
        """Test that triangular without mode raises ValueError."""
        with pytest.raises(ValueError, match="Triangular timing model missing parameters"):
            sample_timing({"type": "triangular", "min": 8.0, "max": 12.0})

    def test_sample_timing_triangular_missing_max_raises_error(self):
        """Test that triangular without max raises ValueError."""
        with pytest.raises(ValueError, match="Triangular timing model missing parameters"):
            sample_timing({"type": "triangular", "min": 8.0, "mode": 10.0})

    def test_sample_timing_exponential_missing_mean_raises_error(self):
        """Test that exponential without mean raises ValueError."""
        with pytest.raises(ValueError, match="Exponential timing model requires 'mean' parameter"):
            sample_timing({"type": "exponential"})

    def test_sample_timing_propagates_validation_errors(self):
        """Test that validation errors from underlying functions are propagated."""
        with pytest.raises(ValueError, match="Fixed timing value must be non-negative"):
            sample_timing({"type": "fixed", "value": -5.0})

        with pytest.raises(ValueError, match="must satisfy min <= mode <= max"):
            sample_timing({"type": "triangular", "min": 10.0, "mode": 5.0, "max": 15.0})

        with pytest.raises(ValueError, match="Exponential mean must be positive"):
            sample_timing({"type": "exponential", "mean": -10.0})


class TestSetRandomSeed:
    """Tests for random seed setting."""

    def test_set_random_seed_produces_deterministic_results(self):
        """Test that setting seed produces deterministic results."""
        set_random_seed(42)
        result1 = sample_exponential(100.0)

        set_random_seed(42)
        result2 = sample_exponential(100.0)

        assert result1 == result2

    def test_set_random_seed_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results."""
        set_random_seed(42)
        result1 = sample_exponential(100.0)

        set_random_seed(123)
        result2 = sample_exponential(100.0)

        assert result1 != result2

    def test_set_random_seed_affects_all_distributions(self):
        """Test that seed affects all distribution types."""
        set_random_seed(42)
        tri1 = sample_triangular(8.0, 10.0, 12.0)
        exp1 = sample_exponential(100.0)

        set_random_seed(42)
        tri2 = sample_triangular(8.0, 10.0, 12.0)
        exp2 = sample_exponential(100.0)

        assert tri1 == tri2
        assert exp1 == exp2

    def test_set_random_seed_sequence_reproducibility(self):
        """Test that sequence of samples is reproducible."""
        set_random_seed(42)
        sequence1 = [sample_exponential(100.0) for _ in range(10)]

        set_random_seed(42)
        sequence2 = [sample_exponential(100.0) for _ in range(10)]

        assert sequence1 == sequence2


class TestIntegration:
    """Integration tests for timing module."""

    def test_multiple_timing_types_in_sequence(self):
        """Test that multiple timing types can be used together."""
        set_random_seed(42)

        fixed = sample_timing({"type": "fixed", "value": 10.0})
        tri = sample_timing({"type": "triangular", "min": 8.0, "mode": 10.0, "max": 12.0})
        exp = sample_timing({"type": "exponential", "mean": 100.0})

        assert fixed == 10.0
        assert 8.0 <= tri <= 12.0
        assert exp > 0

    def test_timing_distribution_statistics(self):
        """Test that timing distributions produce expected statistical properties."""
        set_random_seed(42)

        # Sample 1000 triangular values
        samples = [
            sample_timing({"type": "triangular", "min": 5.0, "mode": 10.0, "max": 15.0})
            for _ in range(1000)
        ]

        # Check bounds
        assert all(5.0 <= s <= 15.0 for s in samples)

        # Mean should be approximately (min + mode + max) / 3
        expected_mean = (5.0 + 10.0 + 15.0) / 3
        actual_mean = np.mean(samples)
        assert abs(actual_mean - expected_mean) / expected_mean < 0.1  # Within 10%
