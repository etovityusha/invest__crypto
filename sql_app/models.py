from sqlalchemy import Boolean, Column, Integer, String, DECIMAL, DateTime

from sql_app.database import Base


class Token(Base):
    __tablename__ = 'token'
    id = Column(Integer, primary_key=True, index=True)
    cmc_id = Column(Integer)
    symbol = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    price = Column(DECIMAL)
    price_last_update = Column(DateTime)

    def __str__(self):
        return self.symbol
