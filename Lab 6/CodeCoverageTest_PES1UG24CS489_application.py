
import pytest
from water_utility_billing import calculate_water_bill, check_meter_tampering


def test_invalid_accounts():
    with pytest.raises(ValueError):
        calculate_water_bill("invalid", 10)


def test_negative_base_fee():
    with pytest.raises(ValueError):
        calculate_water_bill([], -10)


def test_inactive_account():
    result = calculate_water_bill(
        [{"is_active": False}], 10
    )
    assert result["total_billed"] == 0.0


def test_nonpositive_usage():
    accounts = [{
        "is_active": True,
        "usage_blocks": [0, -10]
    }]
    result = calculate_water_bill(accounts, 10)
    assert result["status"] == "NORMAL"


def test_residential_high_usage():
    accounts = [{
        "is_active": True,
        "is_commercial": False,
        "usage_blocks": [120]
    }]
    result = calculate_water_bill(accounts, 10)
    assert result["total_billed"] == 550.0


def test_commercial_high_usage():
    accounts = [{
        "is_active": True,
        "is_commercial": True,
        "usage_blocks": [120]
    }]
    result = calculate_water_bill(accounts, 10)
    assert result["total_billed"] == 430.0


def test_medium_and_low_usage():
    accounts = [{
        "is_active": True,
        "usage_blocks": [60, 30]
    }]
    result = calculate_water_bill(accounts, 10)
    assert result["total_billed"] == 205.0


def test_leak_waiver_applied():
    accounts = [{
        "is_active": True,
        "has_leak_waiver": True,
        "usage_blocks": [100]
    }]
    result = calculate_water_bill(accounts, 10)
    assert result["total_billed"] == 210.0


def test_leak_waiver_not_applied():
    accounts = [{
        "is_active": True,
        "has_leak_waiver": True,
        "usage_blocks": [20]
    }]
    result = calculate_water_bill(accounts, 10)
    assert result["total_billed"] == 40.0


def test_excessive_flags():
    accounts = [{
        "is_active": True,
        "is_commercial": True,
        "usage_blocks": [101, 101, 101, 101, 101, 101]
    }]
    result = calculate_water_bill(accounts, 10)
    assert result["status"] == "EXCESSIVE_FLAGS"


def test_no_activity():
    result = calculate_water_bill([], 10)
    assert result["status"] == "NO_ACTIVITY"


def test_empty_meter_data():
    assert check_meter_tampering([]) == "NO_DATA"


def test_clear_meter_readings():
    assert check_meter_tampering([[10, 20, 30]]) == "CLEAR"


def test_single_negative_reading():
    assert check_meter_tampering([[-10, 20]]) == "CLEAR"


def test_negative_readings_reset():
    assert check_meter_tampering([[-10, 20, -5]]) == "CLEAR"


def test_meter_tampering():
    assert check_meter_tampering([[-10, -20]]) == "TAMPER_SUSPECTED"
