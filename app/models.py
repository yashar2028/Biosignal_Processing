from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = (
    declarative_base()
)  # All the models (classes) that are going to be mapped to database tables have to inherit this.


class SignalAmplitude(Base):
    __tablename__ = "signal_amplitudes"

    id = Column(Integer, primary_key=True)
    first_channel = Column(Float)
    second_channel = Column(Float)
    timestamp = Column(DateTime(timezone=True))


class User(Base):  # User model for SQLAlchemy (table)
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, unique=True, nullable=False)
    last_name = Column(String, unique=True, nullable=False)
    role = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
