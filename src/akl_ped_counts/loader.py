"""
Data loading functions for Auckland pedestrian counts.

All functions return pandas DataFrames with cleaned, ready-to-use data.
"""

from __future__ import annotations

import json
from importlib import resources
from typing import Optional, Sequence

import pandas as pd


def _data_path(filename: str) -> str:
    """Resolve the path to a bundled data file."""
    ref = resources.files("akl_ped_counts") / "data" / filename
    # For older Python (<3.9 compat), fall back to path()
    if hasattr(ref, "__fspath__"):
        return str(ref)
    with resources.as_file(ref) as p:
        return str(p)


# ── Sensor metadata ─────────────────────────────────────────

#: Canonical list of all 21 sensor locations.
SENSORS: list[str] = [
    "107 Quay Street",
    "188 Quay Street Lower Albert (EW)",
    "188 Quay Street Lower Albert (NS)",
    "Te Ara Tahuhu Walkway",
    "Commerce Street West",
    "7 Custom Street East",
    "45 Queen Street",
    "30 Queen Street",
    "19 Shortland Street",
    "2 High Street",
    "1 Courthouse Lane",
    "61 Federal Street",
    "59 High Street",
    "210 Queen Street",
    "205 Queen Street",
    "8 Darby Street EW",
    "8 Darby Street NS",
    "261 Queen Street",
    "297 Queen Street",
    "150 K Road",
    "183 K Road",
]

#: Sensors added in 2022 (not available for 2019-2021).
SENSORS_ADDED_2022: list[str] = [
    "188 Quay Street Lower Albert (EW)",
    "188 Quay Street Lower Albert (NS)",
]


def list_sensors() -> list[str]:
    """Return the canonical list of all 21 sensor location names.

    Returns
    -------
    list of str
        Sensor location names in geographic order (north to south).

    Examples
    --------
    >>> from akl_ped_counts import list_sensors
    >>> sensors = list_sensors()
    >>> len(sensors)
    21
    """
    return SENSORS.copy()


# ── Main data loaders ───────────────────────────────────────

def load_hourly(
    years: Optional[Sequence[int]] = None,
    sensors: Optional[Sequence[str]] = None,
    dropna: bool = False,
) -> pd.DataFrame:
    """Load hourly pedestrian counts.

    Parameters
    ----------
    years : sequence of int, optional
        Filter to specific years (e.g., ``[2022, 2023]``).
        Default loads all years (2019-2025).
    sensors : sequence of str, optional
        Filter to specific sensor locations. Use :func:`list_sensors`
        to see available names. Default loads all sensors.
    dropna : bool, default False
        If True, drop rows containing any missing values in sensor
        columns. Useful for obtaining a complete-cases dataset.

    Returns
    -------
    pd.DataFrame
        Columns: ``date`` (datetime64), ``hour`` (str), ``year`` (int),
        plus one float column per sensor location.

    Examples
    --------
    >>> from akl_ped_counts import load_hourly
    >>> df = load_hourly(years=[2023])
    >>> df.shape
    (8760, 24)

    >>> df_clean = load_hourly(dropna=True)
    """
    df = pd.read_csv(
        _data_path("hourly_counts.csv"),
        parse_dates=["date"],
    )

    if years is not None:
        df = df[df["year"].isin(years)].reset_index(drop=True)

    if sensors is not None:
        keep = ["date", "hour", "year"] + list(sensors)
        df = df[keep]

    if dropna:
        sensor_cols = [c for c in df.columns if c not in ("date", "hour", "year")]
        df = df.dropna(subset=sensor_cols).reset_index(drop=True)

    return df


def load_locations() -> pd.DataFrame:
    """Load sensor location metadata (address, latitude, longitude).

    Returns
    -------
    pd.DataFrame
        Columns: ``Address`` (str), ``Latitude`` (float),
        ``Longitude`` (float). WGS 84 coordinate reference system.
        Contains 21 sensor locations across Auckland CBD.

    Examples
    --------
    >>> from akl_ped_counts import load_locations
    >>> locs = load_locations()
    >>> locs[["Address", "Latitude", "Longitude"]].head(3)
    """
    return pd.read_csv(_data_path("locations.csv"))


def load_daily(
    years: Optional[Sequence[int]] = None,
    sensors: Optional[Sequence[str]] = None,
    dropna: bool = False,
) -> pd.DataFrame:
    """Load daily pedestrian totals (aggregated from hourly data).

    Parameters
    ----------
    years : sequence of int, optional
        Filter to specific years.
    sensors : sequence of str, optional
        Filter to specific sensors.
    dropna : bool, default False
        If True, drop rows with any missing values.

    Returns
    -------
    pd.DataFrame
        Columns: ``date`` (datetime64), ``year`` (int), plus one float
        column per sensor (daily total).

    Examples
    --------
    >>> from akl_ped_counts import load_daily
    >>> daily = load_daily(years=[2024])
    >>> daily.head()
    """
    hourly = load_hourly(years=years, sensors=sensors, dropna=False)
    sensor_cols = [c for c in hourly.columns if c not in ("date", "hour", "year")]

    daily = hourly.groupby(["date", "year"])[sensor_cols].sum(min_count=1)
    daily = daily.reset_index()

    if dropna:
        daily = daily.dropna(subset=sensor_cols).reset_index(drop=True)

    return daily


def load_monthly(
    years: Optional[Sequence[int]] = None,
    sensors: Optional[Sequence[str]] = None,
    dropna: bool = False,
) -> pd.DataFrame:
    """Load monthly pedestrian totals (aggregated from hourly data).

    Parameters
    ----------
    years : sequence of int, optional
        Filter to specific years.
    sensors : sequence of str, optional
        Filter to specific sensors.
    dropna : bool, default False
        If True, drop rows with any missing values.

    Returns
    -------
    pd.DataFrame
        Columns: ``year_month`` (Period[M]), ``year`` (int),
        ``month`` (int), plus one float column per sensor.

    Examples
    --------
    >>> from akl_ped_counts import load_monthly
    >>> monthly = load_monthly()
    >>> monthly.head()
    """
    hourly = load_hourly(years=years, sensors=sensors, dropna=False)
    sensor_cols = [c for c in hourly.columns if c not in ("date", "hour", "year")]

    hourly["year_month"] = hourly["date"].dt.to_period("M")
    hourly["month"] = hourly["date"].dt.month

    monthly = hourly.groupby(["year_month", "year", "month"])[sensor_cols].sum(
        min_count=1
    )
    monthly = monthly.reset_index()

    if dropna:
        monthly = monthly.dropna(subset=sensor_cols).reset_index(drop=True)

    return monthly


# ── Missing data diagnostics ────────────────────────────────

def describe_missing() -> pd.DataFrame:
    """Return a summary of missing data by year and sensor.

    Returns
    -------
    pd.DataFrame
        Multi-indexed by (year, sensor) with columns:
        ``total_hours``, ``missing_hours``, ``pct_missing``.

    Examples
    --------
    >>> from akl_ped_counts import describe_missing
    >>> report = describe_missing()
    >>> report.query("pct_missing > 1")
    """
    report_path = _data_path("missing_data_report.json")
    with open(report_path) as f:
        report = json.load(f)

    rows = []
    for year_str, info in report.items():
        year = int(year_str)
        total_rows = info["rows"]
        for sensor in info["sensor_names"]:
            n_missing = info["per_sensor"].get(sensor, 0)
            rows.append({
                "year": year,
                "sensor": sensor,
                "total_hours": total_rows,
                "missing_hours": n_missing,
                "pct_missing": round(100 * n_missing / total_rows, 2),
            })

    df = pd.DataFrame(rows)
    return df
