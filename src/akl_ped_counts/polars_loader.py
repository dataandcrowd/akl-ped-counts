"""
Polars-based data loading functions for Auckland pedestrian counts.

These mirror the pandas API in :mod:`akl_ped_counts.loader` but return
Polars DataFrames and LazyFrames. Polars must be installed separately::

    pip install polars
    # or
    uv add polars

Usage::

    from akl_ped_counts.polars_loader import load_hourly
    df = load_hourly()  # returns polars.DataFrame
"""

from __future__ import annotations

import json
from typing import Optional, Sequence

try:
    import polars as pl
except ImportError:
    raise ImportError(
        "Polars is required for akl_ped_counts.polars_loader.\n"
        "Install it with: pip install polars  (or: uv add polars)"
    )

from akl_ped_counts.loader import _data_path, SENSORS, SENSORS_ADDED_2022


# ── Main data loaders (Polars) ──────────────────────────────

def load_hourly(
    years: Optional[Sequence[int]] = None,
    sensors: Optional[Sequence[str]] = None,
    dropna: bool = False,
) -> pl.DataFrame:
    """Load hourly pedestrian counts as a Polars DataFrame.

    Parameters
    ----------
    years : sequence of int, optional
        Filter to specific years (e.g., ``[2022, 2023]``).
        Default loads all years (2019-2025).
    sensors : sequence of str, optional
        Filter to specific sensor locations. Use
        :func:`~akl_ped_counts.list_sensors` to see available names.
    dropna : bool, default False
        If True, drop rows containing any null values in sensor columns.

    Returns
    -------
    pl.DataFrame
        Columns: ``date`` (Date), ``hour`` (Utf8), ``year`` (Int64),
        plus one Float64 column per sensor location.

    Examples
    --------
    >>> from akl_ped_counts.polars_loader import load_hourly
    >>> df = load_hourly(years=[2023])
    >>> df.shape
    (8760, 24)
    """
    lf = pl.scan_csv(
        _data_path("hourly_counts.csv"),
        try_parse_dates=True,
    )

    if years is not None:
        lf = lf.filter(pl.col("year").is_in(list(years)))

    if sensors is not None:
        keep = ["date", "hour", "year"] + list(sensors)
        lf = lf.select(keep)

    df = lf.collect()

    if dropna:
        sensor_cols = [c for c in df.columns if c not in ("date", "hour", "year")]
        df = df.drop_nulls(subset=sensor_cols)

    return df


def scan_hourly(
    years: Optional[Sequence[int]] = None,
    sensors: Optional[Sequence[str]] = None,
) -> pl.LazyFrame:
    """Return a Polars LazyFrame for deferred/streaming queries.

    This is useful for large queries where you want to push filters
    and aggregations down before collecting.

    Parameters
    ----------
    years : sequence of int, optional
        Filter to specific years.
    sensors : sequence of str, optional
        Filter to specific sensors.

    Returns
    -------
    pl.LazyFrame

    Examples
    --------
    >>> from akl_ped_counts.polars_loader import scan_hourly
    >>> lf = scan_hourly(years=[2024])
    >>> daily = (
    ...     lf.group_by("date")
    ...     .agg(pl.col("45 Queen Street").sum())
    ...     .sort("date")
    ...     .collect()
    ... )
    """
    lf = pl.scan_csv(
        _data_path("hourly_counts.csv"),
        try_parse_dates=True,
    )

    if years is not None:
        lf = lf.filter(pl.col("year").is_in(list(years)))

    if sensors is not None:
        keep = ["date", "hour", "year"] + list(sensors)
        lf = lf.select(keep)

    return lf


def load_locations() -> pl.DataFrame:
    """Load sensor location metadata as a Polars DataFrame.

    Returns
    -------
    pl.DataFrame
        Columns: ``Address`` (Utf8), ``Latitude`` (Float64),
        ``Longitude`` (Float64). WGS 84 CRS.
    """
    return pl.read_csv(_data_path("locations.csv"))


def load_daily(
    years: Optional[Sequence[int]] = None,
    sensors: Optional[Sequence[str]] = None,
    dropna: bool = False,
) -> pl.DataFrame:
    """Load daily pedestrian totals as a Polars DataFrame.

    Parameters
    ----------
    years : sequence of int, optional
        Filter to specific years.
    sensors : sequence of str, optional
        Filter to specific sensors.
    dropna : bool, default False
        If True, drop rows with any null values.

    Returns
    -------
    pl.DataFrame
        Columns: ``date`` (Date), ``year`` (Int64), plus one Float64
        column per sensor (daily total).
    """
    lf = scan_hourly(years=years, sensors=sensors)
    sensor_cols = [c for c in lf.columns if c not in ("date", "hour", "year")]

    daily = (
        lf.group_by(["date", "year"])
        .agg([pl.col(s).sum() for s in sensor_cols])
        .sort("date")
        .collect()
    )

    if dropna:
        daily = daily.drop_nulls(subset=sensor_cols)

    return daily


def load_monthly(
    years: Optional[Sequence[int]] = None,
    sensors: Optional[Sequence[str]] = None,
    dropna: bool = False,
) -> pl.DataFrame:
    """Load monthly pedestrian totals as a Polars DataFrame.

    Parameters
    ----------
    years : sequence of int, optional
        Filter to specific years.
    sensors : sequence of str, optional
        Filter to specific sensors.
    dropna : bool, default False
        If True, drop rows with any null values.

    Returns
    -------
    pl.DataFrame
        Columns: ``year`` (Int64), ``month`` (Int64), plus one Float64
        column per sensor (monthly total).
    """
    lf = scan_hourly(years=years, sensors=sensors)
    sensor_cols = [c for c in lf.columns if c not in ("date", "hour", "year")]

    monthly = (
        lf.with_columns(pl.col("date").dt.month().alias("month"))
        .group_by(["year", "month"])
        .agg([pl.col(s).sum() for s in sensor_cols])
        .sort(["year", "month"])
        .collect()
    )

    if dropna:
        monthly = monthly.drop_nulls(subset=sensor_cols)

    return monthly


def describe_missing() -> pl.DataFrame:
    """Return a summary of missing data by year and sensor.

    Returns
    -------
    pl.DataFrame
        Columns: ``year``, ``sensor``, ``total_hours``,
        ``missing_hours``, ``pct_missing``.
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

    return pl.DataFrame(rows)
