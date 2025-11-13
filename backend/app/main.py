from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.cors import add_cors
from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.routers import health as health_router
from app.routers import user_inputs as inputs_router
from app.routers import auth as auth_router
from app.routers import market_data as market_router
from app.routers import financial as financial_router

def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await connect_to_mongo()
        try:
            yield
        finally:
            await close_mongo_connection()

    app = FastAPI(title="Goal-Based Hybrid Portfolio Allocation API", version="1.0.0", lifespan=lifespan)
    add_cors(app)
    app.include_router(health_router.router)
    app.include_router(auth_router.router)
    app.include_router(inputs_router.router)
    app.include_router(market_router.router)
    app.include_router(financial_router.router)
    # ML dataset router removed
    return app

app = create_app()