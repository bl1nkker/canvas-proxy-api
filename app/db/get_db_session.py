from db.session import Session


def get_db_session():
    db = Session()
    try:
        yield db
    finally:
        db.close()
