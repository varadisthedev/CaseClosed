from datetime import datetime, timezone


class AsOfError(ValueError):
    """Raised when data observed after the investigation timestamp is used."""


def _epoch(value: datetime) -> float:
    """UTC epoch for order comparisons.

    SQLite round-trips naive (drops timezone info); a naive value is treated as
    UTC so the comparison is valid and consistent between placeholder fixtures
    (aware, from the seed) and values reloaded from the DB (naive).
    """
    if value.tzinfo is None:
        return value.timestamp()
    return value.astimezone(timezone.utc).timestamp()


def guard_record(
    observed_at: datetime | None,
    as_of: datetime | None,
    *,
    label: str = "record",
) -> None:
    """Reject a record whose observation time is after ``as_of``.

    AGENTS.md section 21: historical information must respect the investigation
    timestamp; future benchmark information must not leak into an earlier
    investigation.
    """
    if as_of is None or observed_at is None:
        return
    if _epoch(observed_at) > _epoch(as_of):
        raise AsOfError(
            f"{label} observed at {observed_at.isoformat()} is after as_of "
            f"{as_of.isoformat()}; refusing leak"
        )


def filter_after(
    records: list[dict],
    *,
    as_of: datetime | None,
    time_key: str = "observed_at",
) -> list[dict]:
    """Drop records observed strictly after ``as_of`` (used by integrations)."""
    if as_of is None:
        return list(records)
    kept: list[dict] = []
    for record in records:
        observed = record.get(time_key)
        if observed is None:
            continue
        if isinstance(observed, str):
            observed = datetime.fromisoformat(observed)
        if _epoch(observed) <= _epoch(as_of):
            kept.append(record)
    return kept