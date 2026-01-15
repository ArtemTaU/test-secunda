from fastapi import APIRouter, Request, Depends, HTTPException

from .dependencies import get_db
from .openapi import CHECK_ORGS_IN_BUILDING
from ...domain.schemas import OrgsInBuildingResponse, BuildingAddressQuery
from ...infrastructure.repos.models import Address, Organization

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import (
    select, func
)

from sqlalchemy.orm import selectinload

orgs_router = APIRouter(prefix="/orgs")


@orgs_router.get(
    "/address",
    response_model=OrgsInBuildingResponse,
    **CHECK_ORGS_IN_BUILDING,
)
async def check_orgs_in_building(
        request: Request,
        q: BuildingAddressQuery = Depends(),
        session: AsyncSession = Depends(get_db),
):
    country = q.country.strip()
    city = q.city.strip()
    street = q.street.strip()

    # 1) ищем адрес
    stmt_addr = select(Address.id).where(
        func.lower(Address.country) == func.lower(country),
        func.lower(Address.city) == func.lower(city),
        func.lower(Address.street) == func.lower(street),
        Address.house == q.house,
    )

    if q.building is None:
        stmt_addr = stmt_addr.where(Address.building.is_(None))
    else:
        stmt_addr = stmt_addr.where(Address.building == q.building)

    address_id = (await session.execute(stmt_addr)).scalar_one_or_none()
    if address_id is None:
        raise HTTPException(status_code=404, detail="Здание не найдено.")

    stmt_orgs = (
        select(Organization)
        .where(Organization.address_id == address_id)
        .options(
            selectinload(Organization.address),
            selectinload(Organization.phones),
            selectinload(Organization.activities),
        )
        .order_by(Organization.name)
    )

    orgs = (await session.execute(stmt_orgs)).scalars().all()

    result = []
    for o in orgs:
        result.append(
            {
                "id": o.id,
                "name": o.name,
                "address": o.address,
                "phones": [p.phone for p in o.phones],
                "activities": [a.name for a in o.activities],
            }
        )

    request.app.state.logger.debug(f"Result: {result}")
    return {"organizations": result}
