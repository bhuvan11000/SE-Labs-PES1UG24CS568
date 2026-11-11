"""Property-based fuzz tests for the Lab 7 parking fee functions.

The tests describe the contract of each function:

* valid inputs must produce the documented result, and
* invalid inputs must be rejected with a clear ``ValueError`` instead of
  leaking ``AttributeError``, ``KeyError``, ``IndexError`` or returning a
  nonsensical value.

Hypothesis generates the inputs, so the tests explore far more edge cases
than a handful of hand-written examples could.

Run from this directory with::

    pytest test_parking_fee.py -v
"""

import re

import pytest
from hypothesis import given, settings, strategies as st

from parking_fee import RATES, format_plate, hourly_rate, minutes_parked

# Keep each test quick enough for a lab machine while still exploring plenty
# of generated inputs.  A failing example is printed once so the output stays
# readable when several functions are buggy.
FUZZ = settings(max_examples=100, deadline=None, report_multiple_bugs=False)

FORMATTED_PLATE = re.compile(r"^[A-Z]{2} [0-9]{2} [A-Z]{2} [0-9]{4}$")


# ---------------------------------------------------------------------------
# minutes_parked
# ---------------------------------------------------------------------------

@st.composite
def valid_time_ranges(draw):
    """Generate a same-day entry/exit pair and its expected duration."""
    start = draw(st.integers(min_value=0, max_value=23 * 60 + 59))
    end = draw(st.integers(min_value=start, max_value=23 * 60 + 59))
    times = (
        "{:02d}:{:02d}-{:02d}:{:02d}".format(
            start // 60, start % 60, end // 60, end % 60
        )
    )
    return times, end - start


@FUZZ
@given(valid_time_ranges())
def test_minutes_parked_valid_range(case):
    times, expected = case
    assert minutes_parked(times) == expected


@FUZZ
@given(st.text() | st.none())
def test_minutes_parked_handles_arbitrary_input(raw):
    try:
        minutes = minutes_parked(raw)
    except ValueError:
        return  # invalid input was rejected safely
    assert isinstance(minutes, int)
    assert minutes >= 0


INVALID_TIMES = [
    "",
    "09:30",
    "09:30-11:45-12:00",
    "24:00-25:00",
    "09:60-10:00",
    "11:45-09:30",
    "aa:bb-cc:dd",
]


@FUZZ
@given(st.sampled_from(INVALID_TIMES))
def test_minutes_parked_rejects_invalid_input(raw):
    with pytest.raises(ValueError):
        minutes_parked(raw)


# ---------------------------------------------------------------------------
# hourly_rate
# ---------------------------------------------------------------------------

@FUZZ
@given(st.sampled_from(sorted(RATES)))
def test_hourly_rate_known_vehicles(vehicle):
    assert hourly_rate("  " + vehicle.upper() + "  ") == RATES[vehicle]


@FUZZ
@given(st.text() | st.none())
def test_hourly_rate_handles_arbitrary_input(raw):
    try:
        rate = hourly_rate(raw)
    except ValueError:
        return  # unknown or non-text vehicle was rejected safely
    assert rate in RATES.values()


INVALID_VEHICLES = ["bus", "plane", "truck!", "123", "bike car"]


@FUZZ
@given(st.sampled_from(INVALID_VEHICLES))
def test_hourly_rate_rejects_unknown_vehicle(raw):
    with pytest.raises(ValueError):
        hourly_rate(raw)


# ---------------------------------------------------------------------------
# format_plate
# ---------------------------------------------------------------------------

@FUZZ
@given(st.from_regex(r"[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}", fullmatch=True))
def test_format_plate_valid_plates(plate):
    expected = "{} {} {} {}".format(
        plate[:2], plate[2:4], plate[4:6], plate[6:]
    )
    assert format_plate(plate) == expected


@FUZZ
@given(st.text() | st.none())
def test_format_plate_handles_arbitrary_input(raw):
    try:
        formatted = format_plate(raw)
    except ValueError:
        return  # malformed plate was rejected safely
    assert FORMATTED_PLATE.fullmatch(formatted)


INVALID_PLATES = [
    "KA01AB123",
    "KA01AB12345",
    "K101AB1234",
    "KA01AB123X",
    "not-a-plate",
]


@FUZZ
@given(st.sampled_from(INVALID_PLATES))
def test_format_plate_rejects_invalid_plate(raw):
    with pytest.raises(ValueError):
        format_plate(raw)
