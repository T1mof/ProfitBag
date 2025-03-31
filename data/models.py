from sqlalchemy import Column, Integer, Text, String, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Text, nullable=False, unique=True)

class UserCoin(Base):
    __tablename__ = 'user_coins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    coin = Column(String(10), nullable=False)
    amount = Column(Numeric(18, 8), nullable=False)
    purchase_price = Column(Numeric(18, 8), nullable=False)
