from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, index=True)
    description = Column(String)
    is_income = Column(Boolean, default=False)
    date = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    owner = relationship("User", back_populates="transactions")