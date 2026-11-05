import pytest

from pppm_elm369 import PurplePoolScheduler


@pytest.fixture
def scheduler():
    return PurplePoolScheduler()


def test_purple_pool_priority_boost(scheduler):
    priority_aligned = scheduler.calculate_priority(
        "Core Telemetry Upgrade", 2.0, is_purple_pool_aligned=True
    )
    priority_unaligned = scheduler.calculate_priority(
        "Standard Background Sweep", 2.0, is_purple_pool_aligned=False
    )

    assert priority_aligned == 5.0
    assert priority_unaligned == 2.0


def test_charity_allocation_split_conserves_total(scheduler):
    ledger = scheduler.process_charity_allocation(1000.0)

    assert len(ledger) == 3
    assert sum(ledger.values()) == 10.0
    assert list(ledger.values()) == [3.34, 3.33, 3.33]
    assert "Shriners Hospitals for Children" in ledger


@pytest.mark.parametrize("value", [-1.0, float("nan"), float("inf")])
def test_charity_allocation_rejects_invalid_values(scheduler, value):
    with pytest.raises(ValueError):
        scheduler.process_charity_allocation(value)


@pytest.mark.parametrize("weight", [-1.0, float("nan"), float("inf")])
def test_priority_rejects_invalid_weights(scheduler, weight):
    with pytest.raises(ValueError):
        scheduler.calculate_priority("Invalid task", weight, True)
