"""
auckland-pedestrian
===================

Hourly pedestrian count data from Heart of the City Auckland's pedestrian
monitoring system, covering 21 sensor locations across Auckland CBD
(2019-2025).

Quick start::

    >>> from auckland_pedestrian import load_hourly, load_locations
    >>> counts = load_hourly()
    >>> locations = load_locations()

Data source: Heart of the City Auckland
https://www.hotcity.co.nz/pedestrian-counts
Licensed under CC BY 4.0.

Polars support::

    from auckland_pedestrian.polars_loader import load_hourly
    counts = load_hourly()  # returns polars.DataFrame
"""

from auckland_pedestrian.loader import (
    load_hourly,
    load_locations,
    load_daily,
    load_monthly,
    list_sensors,
    describe_missing,
    SENSORS,
    SENSORS_ADDED_2022,
)

__version__ = "0.1.0"

__all__ = [
    "load_hourly",
    "load_locations",
    "load_daily",
    "load_monthly",
    "list_sensors",
    "describe_missing",
    "SENSORS",
    "SENSORS_ADDED_2022",
    "__version__",
]
