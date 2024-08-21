from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.transaction import Transaction
from app.api.schemas import transaction 

async def create_transaction(transaction: transaction.Transaction,user_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        transaction_data = transaction.dict()
        db_transaction = Transaction(**transaction_data, user_id=user_id)
        session.add(db_transaction)
        await session.commit()
        await session.refresh(db_transaction)
        return db_transaction
    
async def read_transactions(db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Transaction))
        transactions = result.scalars().all()
        return transactions
    
async def get_transactions_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        # Query for transactions related to the specific user
        result = await session.execute(select(Transaction).filter(Transaction.user_id == user_id))
        transactions = result.scalars().all()
        
        return transactions
    
async def read_by_id_transactions(transaction_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session: 
        result = await session.execute(select(Transaction).filter(Transaction.id == transaction_id))
        transaction = result.scalars().first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    
async def update_transaction(transaction_id: int, transaction: transaction.Transaction, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Transaction).filter(Transaction.id == transaction_id))
        db_transaction = result.scalars().first()
        if not db_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        for key, value in transaction.dict().items():
            setattr(db_transaction, key, value)
        await session.commit()
        await session.refresh(db_transaction)
        return db_transaction
    
async def delete_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Transaction).filter(Transaction.id == transaction_id))
        db_transaction = result.scalars().first()
        if not db_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        await session.delete(db_transaction)
        await session.commit()
        return db_transaction