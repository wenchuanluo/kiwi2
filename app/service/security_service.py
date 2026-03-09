from typing import List

from app.db import db
from app.models import Security


class SecurityException(Exception):
    pass


def get_all_securities() -> List[Security]:
    # CHANGED: removed try/except and rollback
    securities = db.session.query(Security).all()
    return securities


def get_security_by_ticker(ticker: str) -> Security | None:
    # CHANGED: removed try/except and rollback
    security = db.session.query(Security).filter_by(ticker=ticker).one_or_none()
    return security