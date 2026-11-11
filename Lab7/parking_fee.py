"""Parking fee helpers used in Lab 7 (fuzz testing).

The original functions assumed that every argument had the exact expected
shape.  A malformed value therefore leaked low-level exceptions such as
``AttributeError``, ``KeyError`` or ``IndexError``.  The public functions now
validate their input up front and raise a descriptive ``ValueError`` for
anything they cannot process.

Run the interactive demo with::

    python parking_fee.py
"""

import re

RATES = {"bike": 10, "car": 30, "truck": 60}

_PLATE_PATTERN = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$")


def _parse_clock(value):
    """Convert a ``HH:MM`` string to minutes after midnight.

    Both ``09:30`` and ``9:30`` are accepted.  Anything else raises
    ``ValueError`` with a message that explains what was expected.
    """
    pieces = value.split(":")
    if len(pieces) != 2:
        raise ValueError("time must use the HH:MM format, got {!r}".format(value))

    hour_text, minute_text = pieces
    if not (hour_text.isascii() and hour_text.isdigit()):
        raise ValueError("hours must be digits, got {!r}".format(hour_text))
    if not (minute_text.isascii() and minute_text.isdigit()):
        raise ValueError("minutes must be digits, got {!r}".format(minute_text))
    if not (1 <= len(hour_text) <= 2 and len(minute_text) == 2):
        raise ValueError("time must use the HH:MM format, got {!r}".format(value))

    hour = int(hour_text)
    minute = int(minute_text)
    if not 0 <= hour <= 23:
        raise ValueError("hours must be between 00 and 23, got {:02d}".format(hour))
    if not 0 <= minute <= 59:
        raise ValueError("minutes must be between 00 and 59, got {:02d}".format(minute))
    return hour * 60 + minute


def minutes_parked(times):
    """Return the number of minutes between an entry and exit time.

    ``times`` must be a string such as ``"09:30-11:45"``.  The exit time must
    be on the same day as, or later than, the entry time.
    """
    if not isinstance(times, str):
        raise ValueError(
            "times must be a string in HH:MM-HH:MM format, got {!r}".format(times)
        )

    parts = times.strip().split("-")
    if len(parts) != 2:
        raise ValueError(
            "times must contain exactly one '-' separator, got {!r}".format(times)
        )

    entry_text, exit_text = (part.strip() for part in parts)
    if not entry_text or not exit_text:
        raise ValueError(
            "both entry and exit times are required, got {!r}".format(times)
        )

    entry = _parse_clock(entry_text)
    exit_time = _parse_clock(exit_text)
    if exit_time < entry:
        raise ValueError(
            "exit time must not be earlier than entry time, got {!r}".format(times)
        )
    return exit_time - entry


def hourly_rate(vehicle):
    """Return the hourly rate for a supported vehicle type."""
    if not isinstance(vehicle, str):
        raise ValueError(
            "vehicle type must be a string (bike, car or truck), "
            "got {!r}".format(vehicle)
        )

    key = vehicle.strip().lower()
    if key not in RATES:
        raise ValueError(
            "unsupported vehicle type {!r}; expected one of: {}".format(
                vehicle, ", ".join(sorted(RATES))
            )
        )
    return RATES[key]


def format_plate(plate):
    """Normalise an Indian number plate to ``"KA 01 AB 1234"`` form."""
    if not isinstance(plate, str):
        raise ValueError("number plate must be a string, got {!r}".format(plate))

    # Accept common separators and lowercase input, but validate the core
    # format before indexing into the string.
    cleaned = "".join(plate.split()).replace("-", "").upper()
    if not _PLATE_PATTERN.fullmatch(cleaned):
        raise ValueError(
            "number plate must be 2 letters, 2 digits, 2 letters and 4 digits "
            "(for example KA01AB1234), got {!r}".format(plate)
        )

    return "{} {} {} {}".format(
        cleaned[:2], cleaned[2:4], cleaned[4:6], cleaned[6:]
    )


def _ask(prompt, function, label):
    """Read one value, run a parser, and report errors without crashing."""
    raw = input(prompt)
    try:
        result = function(raw)
    except ValueError as exc:
        print("Invalid input:", exc)
    else:
        print("{}:".format(label), result)


def main():
    print("==== Running minutes_parked ====")
    _ask(
        "Enter entry and exit time (e.g. 09:30-11:45): ",
        minutes_parked,
        "Minutes Parked",
    )

    print("\n==== Running hourly_rate ====")
    _ask(
        "Enter vehicle type (bike/car/truck): ",
        hourly_rate,
        "Hourly Rate",
    )

    print("\n==== Running format_plate ====")
    _ask(
        "Enter a number plate (e.g. ka01ab1234): ",
        format_plate,
        "Formatted Plate",
    )


if __name__ == "__main__":
    main()
