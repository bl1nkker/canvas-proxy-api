from cleo import Command
from sqlalchemy import create_engine, text
from sqlalchemy.engine import ResultProxy
from sqlalchemy.pool import NullPool

from db.config import get_db_config


class DbInitCommand(Command):
    name = "dbinit"
    description = "Initializes database according to environment variables, yaml file and passed defaults"

    def handle(self):
        db_config = get_db_config()
        postgres_engine = create_engine(db_config.postgres_url(), poolclass=NullPool)

        with postgres_engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text(
                        f"""DO $$
                    BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{db_config.app_db_user}') THEN
                        CREATE ROLE {db_config.app_db_user} LOGIN PASSWORD '{db_config.app_db_pass}';
                    END IF;
                    END
                    $$;"""
                    )
                )

        with postgres_engine.connect() as conn:
            # committing transaction immediately to be able to create database
            conn.execute(text("COMMIT"))

            result: ResultProxy = conn.execute(
                text(
                    f"SELECT 1 FROM pg_database WHERE datname = '{db_config.app_db_name}'"
                )
            )
            exists = result.first()
            if not exists:
                conn.execute(
                    text(
                        f"CREATE DATABASE {db_config.app_db_name} WITH OWNER = {db_config.app_db_user}"
                    )
                )

        # no need to keep engine with postgres permissions anymore
        postgres_engine.dispose()

        # su conn for app db
        postgres_engine = create_engine(db_config.postgres_url(for_app_db=True), poolclass=NullPool)
        with postgres_engine.connect() as conn:
            # Create vector extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.execute(text("COMMIT"))

        postgres_engine.dispose()

        app_engine = create_engine(db_config.app_url(), poolclass=NullPool)
        with app_engine.connect() as conn:
            conn.execute(
                text(
                    f"CREATE SCHEMA IF NOT EXISTS app AUTHORIZATION {db_config.app_db_user}"
                )
            )
            conn.execute(text("COMMIT"))
