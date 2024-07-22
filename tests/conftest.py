import asyncio
import os
from functools import lru_cache

import pytest
from alembic import command
from alembic.config import Config
from faker import Faker

fake = Faker()


@lru_cache
def get_alembic_cfg():
    alembic_cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))

    if not os.path.isfile(alembic_cfg_path):
        raise FileNotFoundError(f"Configuration file not found at: {alembic_cfg_path}")

    alembic_cfg = Config(alembic_cfg_path)
    alembic_cfg.set_main_option(
        "script_location", os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'alembic'))
    )
    return alembic_cfg


def run_migrations(alembic_cfg):
    command.upgrade(alembic_cfg, "head")
    command.revision(alembic_cfg, message="create test tables", autogenerate=True)
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    alembic_cfg = get_alembic_cfg()
    run_migrations(alembic_cfg)


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def user_json():
    return {
        "email": fake.email(),
        "password": fake.password(),
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "fullname": "string",
        "nickname": fake.user_name()
    }
