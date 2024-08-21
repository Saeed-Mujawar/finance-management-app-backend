from pydantic import BaseModel
from typing import List

class TransactionBase(BaseModel):
    amount: float
    category: str
    description: str
    is_income: bool
    date: str

class Transaction(TransactionBase):
    class Config:
        orm_mode = True

class ReadTransaction(Transaction):
    id: int 
    class Config:
        orm_mode = True


class ShowUser(BaseModel):
    id: int
    username: str
    email: str
    role: str
    transactions: List[Transaction]
    class Config:
        orm_mode = True 

class ShowTransaction(TransactionBase):
    owner: 'ShowUser' # Forward declaration to avoid circular import
    class Config:
        orm_mode = True 

