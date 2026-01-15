from alchemium import UnitOfWork
from fastapi import Request


def get_uow(request: Request) -> UnitOfWork:
    return UnitOfWork(request.app.state.session_maker)
