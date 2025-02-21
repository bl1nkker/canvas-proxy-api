from cleo import Command
from sqlalchemy import create_engine, text
from sqlalchemy.engine import ResultProxy
from sqlalchemy.pool import NullPool

from db.config import get_db_config


class DbDropCommand(Command):
    name = "dbdrop"
    description = "Drops database according to environment variables, yaml file and passed defaults"

    def handle(self):
        db_config = get_db_config()
        postgres_engine = create_engine(db_config.postgres_url(), poolclass=NullPool)

        # drop database first
        with postgres_engine.connect() as conn:
            # committing transaction immediately to be able to drop database
            conn.execute(text("COMMIT"))

            result: ResultProxy = conn.execute(
                text(
                    f"SELECT 1 FROM pg_database WHERE datname = '{db_config.app_db_name}'"
                )
            )
            exists = result.first()
            if exists:
                conn.execute(text(f"DROP DATABASE {db_config.app_db_name}"))

        # drop user
        with postgres_engine.connect() as conn:
            with conn.begin():
                conn.execute(text(f"DROP ROLE IF EXISTS {db_config.app_db_user}"))
