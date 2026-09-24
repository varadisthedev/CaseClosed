from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import RunStatus
from app.db.models import InvestigationRun, InvestigationStep


class RunRepository:
    """Persistence for LangGraph investigation runs and their step log."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_run(
        self,
        *,
        run_id: str,
        case_id: str,
        agent_version: str = "0.1.0",
        policy_version: str = "1.0",
    ) -> InvestigationRun:
        run = InvestigationRun(
            run_id=run_id,
            case_id=case_id,
            status=RunStatus.PENDING,
            agent_version=agent_version,
            policy_version=policy_version,
        )
        self.session.add(run)
        return run

    def get_run(self, run_id: str) -> InvestigationRun | None:
        return self.session.scalar(
            select(InvestigationRun).where(InvestigationRun.run_id == run_id)
        )

    def add_step(
        self, run_id: str, step_index: int, node_name: str, payload: dict[str, Any]
    ) -> InvestigationStep:
        step = InvestigationStep(
            run_id=run_id,
            step_index=step_index,
            node_name=node_name,
            payload=payload,
        )
        self.session.add(step)
        return step

    def list_steps(self, run_id: str) -> list[InvestigationStep]:
        stmt = (
            select(InvestigationStep)
            .where(InvestigationStep.run_id == run_id)
            .order_by(InvestigationStep.step_index)
        )
        return list(self.session.scalars(stmt).all())

    def update_run(self, run_id: str, **values: Any) -> InvestigationRun | None:
        run = self.get_run(run_id)
        if run is None:
            return None
        for key, value in values.items():
            if hasattr(run, key):
                setattr(run, key, value)
        return run