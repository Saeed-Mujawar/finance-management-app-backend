from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.core.database import engine, create_all

from app.api.routers import transaction, user, authentication


app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "final API is working"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup():
    await create_all()



app.include_router(authentication.router, prefix="/auth", tags=["auth"])
app.include_router(transaction.router, prefix="/transactions", tags=["transactions"])
app.include_router(user.router, prefix="/users", tags=["users"])
