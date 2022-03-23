from sqlalchemy import Boolean, Column, Integer, String
from sql_app.database import Base


class Token(Base):
    __tablename__ = 'token'
    cmc_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    def __str__(self):
        return self.symbol
