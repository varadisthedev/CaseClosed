import os
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def _isolated_env() -> Generator[None, None, None]:
    """Force a throwaway SQLite DB and placeholder backends for the suite."""
    tmp = tempfile.NamedTemporaryFile(prefix="caseclosed_test_", suffix=".sqlite", delete=False)
    tmp.close()
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp.name}"
    os.environ["USE_PLACEHOLDERS"] = "true"
    os.environ["APP_ENV"] = "test"
    os.environ["API_KEY"] = ""
    yield
    try:
        os.unlink(tmp.name)
    except OSError:
        pass


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    from app.core.config import get_settings
    from app.db.session import reset_engine
    from app.main import create_app

    get_settings.cache_clear()
    reset_engine()
    app = create_app()
    with TestClient(app) as c:
        yield c
    reset_engine()
    get_settings.cache_clear()