import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

os.environ["TESTING"] = "true"

from src.db.base import Base
from src.db.session import get_db
from src.main import app
from src.models.user import User, Role
from src.models.financial_record import FinancialRecord  # ensures model is registered
from src.core.security import hash_password

TEST_DB_URL = "sqlite:///./test_finance.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def attach_finance_schema(conn, _):
    conn.execute("ATTACH DATABASE 'test_finance_schema.db' AS finance")


SessionTest = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    for f in ("test_finance.db", "test_finance_schema.db"):
        if os.path.exists(f):
            os.remove(f)


@pytest.fixture()
def db():
    session = SessionTest()
    try:
        yield session
    finally:
        session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db):
    user = User(
        email="testadmin@example.com",
        full_name="Test Admin",
        hashed_password=hash_password("adminpass"),
        role=Role.admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def viewer_user(db):
    user = User(
        email="testviewer@example.com",
        full_name="Test Viewer",
        hashed_password=hash_password("viewerpass"),
        role=Role.viewer,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def admin_token(client, admin_user):
    resp = client.post("/auth/login", json={"email": "testadmin@example.com", "password": "adminpass"})
    return resp.json()["access_token"]


@pytest.fixture()
def analyst_user(db):
    user = User(
        email="testanalyst@example.com",
        full_name="Test Analyst",
        hashed_password=hash_password("analystpass"),
        role=Role.analyst,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def analyst_token(client, analyst_user):
    resp = client.post("/auth/login", json={"email": "testanalyst@example.com", "password": "analystpass"})
    return resp.json()["access_token"]


@pytest.fixture()
def viewer_token(client, viewer_user):
    resp = client.post("/auth/login", json={"email": "testviewer@example.com", "password": "viewerpass"})
    return resp.json()["access_token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
