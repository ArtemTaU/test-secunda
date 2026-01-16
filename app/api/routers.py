from fastapi import APIRouter, Request, Depends, HTTPException

from app.infrastructure.dependencies import get_db
from .mappers.organizations import orgs_to_out
from .openapi import CHECK_ORGS_IN_BUILDING
from app.api.schemas import OrgsInBuildingResponse, BuildingAddressQuery
from app.infrastructure.repos.cruds import AddressRepository, OrganizationRepository

from sqlalchemy.ext.asyncio import AsyncSession


orgs_router = APIRouter(prefix="/orgs")
addresses_router = APIRouter(prefix="/addresses")


@orgs_router.get(
    "",
    response_model=OrgsInBuildingResponse,
    #**GET_ALL_ORGS,
)
async def get_all_orgs(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    org_repo = OrganizationRepository(session)
    orgs = await org_repo.list_all()

    result = [
        {
            "id": o.id,
            "name": o.name,
            "address": o.address,
            "phones": [p.phone for p in o.phones],
            "activities": [a.name for a in o.activities],
        }
        for o in orgs
    ]

    return {"organizations": result}



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
    house = q.house
    building = q.building

    address_repo = AddressRepository(session)
    org_repo = OrganizationRepository(session)

    address_id = await address_repo.get_address_id(
        country=country,
        city=city,
        street=street,
        house=house,
        building=building,
    )

    if address_id is None:
        raise HTTPException(status_code=404, detail="Здание не найдено.")

    orgs = await org_repo.list_by_address(address_id)

    result = orgs_to_out(orgs)
    return {"organizations": result}


@addresses_router.get(
    "",
    #**GET_ALL_ADDRESSES,
)
async def get_all_addresses(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    address_repo = AddressRepository(session)
    addresses = await address_repo.list_all()

    result = [
        {
            "id": a.id,
            "country": a.country,
            "city": a.city,
            "street": a.street,
            "house": a.house,
            "building": a.building,
        }
        for a in addresses
    ]

    request.app.state.logger.debug(f"Result: {result}")
    return {"addresses": result}