
import pytest
from water_utility_billing import calculate_water_bill, check_meter_tampering


# Input validation branches

def test_invalid_accounts_type():
    with pytest.raises(ValueError):
        calculate_water_bill("invalid", 10)


def test_negative_base_fee():
    with pytest.raises(ValueError):
        calculate_water_bill([], -10)


def test_valid_empty_accounts():
    result = calculate_water_bill([], 10)
    assert result["status"] == "NO_ACTIVITY"


# Account activity and usage loop branches

def test_inactive_account():
    result = calculate_water_bill(
        [{"is_active": False, "usage_blocks": [100]}], 10
    )
    assert result["total_billed"] == 0.0


def test_active_account_with_empty_usage():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": []}], 10
    )
    assert result["total_billed"] == 10.0
    assert result["status"] == "NORMAL"


def test_zero_and_negative_usage():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [0, -10]}], 10
    )
    assert result["status"] == "NORMAL"
    assert result["total_billed"] == 10.0


# Residential and commercial billing branches

def test_residential_usage_above_100():
    result = calculate_water_bill(
        [{
            "is_active": True,
            "is_commercial": False,
            "usage_blocks": [120, 20]
        }], 10
    )
    assert result["total_billed"] == 550.0


def test_commercial_usage_above_100():
    result = calculate_water_bill(
        [{
            "is_active": True,
            "is_commercial": True,
            "usage_blocks": [120]
        }], 10
    )
    assert result["total_billed"] == 430.0


def test_usage_between_51_and_100():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [60]}], 10
    )
    assert result["total_billed"] == 160.0


def test_usage_at_most_50():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [30]}], 10
    )
    assert result["total_billed"] == 55.0


def test_multiple_usage_tiers():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [20, 60, 120]}], 10
    )
    assert result["total_billed"] == 730.0


# Leak waiver branches

def test_leak_waiver_above_200():
    result = calculate_water_bill(
        [{
            "is_active": True,
            "has_leak_waiver": True,
            "usage_blocks": [100]
        }], 10
    )
    assert result["total_billed"] == 210.0


def test_leak_waiver_at_most_200():
    result = calculate_water_bill(
        [{
            "is_active": True,
            "has_leak_waiver": True,
            "usage_blocks": [20]
        }], 10
    )
    assert result["total_billed"] == 40.0


def test_no_leak_waiver():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [100]}], 10
    )
    assert result["total_billed"] == 260.0


# Billing status branches

def test_excessive_flags():
    result = calculate_water_bill(
        [{
            "is_active": True,
            "is_commercial": True,
            "usage_blocks": [101, 101, 101, 101, 101, 101]
        }], 10
    )
    assert result["status"] == "EXCESSIVE_FLAGS"


def test_normal_status():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [20]}], 10
    )
    assert result["status"] == "NORMAL"


def test_no_activity_status():
    result = calculate_water_bill([], 10)
    assert result["status"] == "NO_ACTIVITY"


# Meter tampering branches

def test_empty_readings_matrix():
    assert check_meter_tampering([]) == "NO_DATA"


def test_empty_individual_meter():
    assert check_meter_tampering([[]]) == "CLEAR"


def test_positive_readings():
    assert check_meter_tampering([[10, 20, 30]]) == "CLEAR"


def test_single_negative_reading():
    assert check_meter_tampering([[-10, 20]]) == "CLEAR"


def test_negative_counter_resets():
    assert check_meter_tampering([[-10, 20, -5]]) == "CLEAR"


def test_two_consecutive_negative_readings():
    assert check_meter_tampering([[-10, -20]]) == "TAMPER_SUSPECTED"


def test_tampering_in_second_meter():
    assert check_meter_tampering([[10, 20], [-5, -10]]) == "TAMPER_SUSPECTED"
