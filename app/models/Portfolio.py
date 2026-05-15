from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import db

if TYPE_CHECKING:
    from app.models import Investment, Transaction, User


class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    owner: Mapped[str] = mapped_column(String(30), ForeignKey('user.username'), nullable=False)

    investments: Mapped[List['Investment']] = relationship('Investment', back_populates='portfolio', lazy='selectin')

    user: Mapped['User'] = relationship('User', foreign_keys=[owner], back_populates='portfolios', lazy='selectin')

    transactions: Mapped[List['Transaction']] = relationship('Transaction', back_populates='portfolio', lazy='selectin')

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            name: str | None = None,
            user: User | None = None,
            description: str | None = None,
            id: int | None = None,
        ) -> None: ...

    def __str__(self):
        user_str = getattr(self, 'user', None)
        username = user_str.username if user_str else 'N/A'
        investments = []
        for investment in self.investments:
            investments.append(
                {
                    'ticker': investment.ticker,
                    'quantity': investment.quantity,
                }
            )
        return f'<Portfolio: id={self.id}; name={self.name}; description={self.description}; user={username}; investments={", ".join(str(i) for i in investments)}>'

    def __to_dict__(self, current_user: str | None = None):
        investments = []
        for investment in self.investments:
            investments.append(
                {
                    'ticker': investment.ticker,
                    'quantity': investment.quantity,
                }
            )
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner': self.owner,
            'investments_count': len(self.investments),
            'investments': investments,
        }

        if current_user is not None:
            result['my_role'] = self._compute_role(current_user)

        return result

    def _compute_role(self, username: str) -> str:
        """
        Determine the given user's role for this portfolio.
        Returns one of: 'owner', 'manager', 'viewer', 'none'.
        """
        if self.owner == username:
            return 'owner'

        # Delayed import to avoid circular dependency
        from app.models import PortfolioSecurity
        access = db.session.query(PortfolioSecurity).filter_by(
            portfolio_id=self.id,
            username=username,
        ).one_or_none()

        if access is None:
            return 'none'
        return access.role