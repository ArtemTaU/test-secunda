from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

from app.infrastructure.core import settings
from app.infrastructure.core import lifespan
from app.presentation.api.routers import orgs_router


def create_app() -> FastAPI:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ]

    fastapi_app = FastAPI(
        title=settings.app_title,
        debug=settings.debug,
        summary=settings.summary or None,
        description=settings.description or None,
        version=settings.version or "0.0.0",
        middleware=middleware,
        lifespan=lifespan,
        root_path=settings.root_path or "",
    )
    fastapi_app.include_router(orgs_router)

    if settings.debug:
        @fastapi_app.get("/info")
        async def app_info():
            return {**settings.model_dump()}

    return fastapi_app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
