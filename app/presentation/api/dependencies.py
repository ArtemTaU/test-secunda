from fastapi import Request


async def get_db(request: Request):
    # тут оверхед, но для реальных транзакций надо (желательно даже правильно ловить исключения)
    session_maker = request.app.state.session_maker
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()