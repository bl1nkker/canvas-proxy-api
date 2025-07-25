from sqlalchemy import TIMESTAMP, BigInteger, Column, Integer, String, func, text


class HasWebId:
    web_id = Column(String(32), unique=True, nullable=False)


class DbModel:
    id = Column(BigInteger, primary_key=True)
    version_id = Column(Integer, nullable=False, default=1)
    created_date = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_date = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=func.now(),
    )

    __table_args__ = ({"schema": "app"},)
    __mapper_args__ = {"version_id_col": version_id}

    @classmethod
    def get_table_args(cls) -> dict:
        return {"schema": "app"}
