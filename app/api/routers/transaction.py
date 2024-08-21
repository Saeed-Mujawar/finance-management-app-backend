from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import transaction, user
from app.services import transaction as transactionRepo
from app.core.database import get_db
from app.core import oaut2

router = APIRouter()

@router.post("/", response_model=transaction.ReadTransaction, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: transaction.Transaction,
    db: AsyncSession = Depends(get_db),
    current_user: user.User = Depends(oaut2.get_current_user)
):
    return await transactionRepo.create_transaction(transaction, current_user.id, db)

@router.get("/", response_model=list[transaction.ReadTransaction])
async def read_transactions(
    db: AsyncSession = Depends(get_db),
    current_user: user.User = Depends(oaut2.get_current_user)
):
    return await transactionRepo.get_transactions_by_user(current_user.id, db)

@router.get("/{transaction_id}", response_model=transaction.ReadTransaction)
async def get_transaction(
    transaction_id: int, 
    db: AsyncSession = Depends(get_db)
):
    return await transactionRepo.read_by_id_transactions(transaction_id, db)

@router.put("/{transaction_id}", response_model=transaction.ReadTransaction)
async def update_transaction(
    transaction_id: int,
    transaction: transaction.Transaction,
    db: AsyncSession = Depends(get_db)
):
    return await transactionRepo.update_transaction(transaction_id, transaction, db)

@router.delete("/{transaction_id}", response_model=transaction.ReadTransaction)
async def delete_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await transactionRepo.delete_transaction(transaction_id, db)
