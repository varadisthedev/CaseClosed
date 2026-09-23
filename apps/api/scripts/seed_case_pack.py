"""Seed the 20 benchmark cases from case_pack.csv into PostgreSQL.

Usage:
    python -m scripts.seed_case_pack [path/to/case_pack.csv]

Resolution order for the CSV:
    1. CLI argument
    2. $CASE_PACK_PATH
    3. /data/case_pack.csv           (Docker mount)
    4. <repo>/dataset/case_pack.csv  (local dev)
"""

from __future__ import annotations

import asyncio
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.core.enums import TriggerType
from app.db.models import Case
from app.db.session import async_session_maker, engine


def _resolve_path(arg: str | None) -> Path:
    candidates: list[Path] = []
    if arg:
        candidates.append(Path(arg))
    if os.getenv("CASE_PACK_PATH"):
        candidates.append(Path(os.environ["CASE_PACK_PATH"]))
    candidates.append(Path("/data/case_pack.csv"))
    # Fallback: repo-relative path (only valid outside container)
    try:
        repo_root = Path(__file__).resolve().parents[3]
        candidates.append(repo_root / "dataset" / "case_pack.csv")
    except IndexError:
        pass
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(f"case_pack.csv not found in: {candidates}")


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.strip())


def _load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


async def seed(csv_path: Path) -> int:
    rows = _load_rows(csv_path)
    async with async_session_maker() as session:
        for row in rows:
            risk = (row.get("risk_score") or "").strip()
            values = {
                "case_id": row["case_id"],
                "trigger_type": TriggerType(row["trigger_type"]),
                "trigger_text": row.get("trigger_text", ""),
                "flagged_txn_id": row["flagged_txn_id"],
                "card_id": row["card_id"],
                "customer_id": row["customer_id"],
                "input_risk_score": float(risk) if risk else None,
                "opened_at": _parse_dt(row["opened_at"]),
                "as_of": _parse_dt(row["opened_at"]),
            }
            stmt = insert(Case).values(**values)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Case.case_id],
                set_={
                    "trigger_type": stmt.excluded.trigger_type,
                    "trigger_text": stmt.excluded.trigger_text,
                    "flagged_txn_id": stmt.excluded.flagged_txn_id,
                    "card_id": stmt.excluded.card_id,
                    "customer_id": stmt.excluded.customer_id,
                    "input_risk_score": stmt.excluded.input_risk_score,
                    "opened_at": stmt.excluded.opened_at,
                    "as_of": stmt.excluded.as_of,
                },
            )
            await session.execute(stmt)
        await session.commit()

        count = await session.scalar(select(func.count()).select_from(Case))
    return int(count or 0)


async def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    path = _resolve_path(arg)
    print(f"[seed] Loading case pack from {path}")
    try:
        total = await seed(path)
        print(f"[seed] Done. total cases in table: {total}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())