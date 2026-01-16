from fastapi import APIRouter, Request, Depends, HTTPException, Path

from app.infrastructure.dependencies import get_db
from .mappers.addresses import addresses_to_out
from .mappers.organizations import orgs_to_out, org_to_out
from .openapi import CHECK_ORGS_IN_BUILDING, GET_ALL_ORGS, GET_ALL_ADDRESSES, GET_ORG_BY_ID
from app.api.schemas import OrgsInBuildingResponse, BuildingAddressQuery, AddressOut, AddressesResponse, OrganizationOut
from app.infrastructure.repos.cruds import AddressRepository, OrganizationRepository

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

orgs_router = APIRouter(prefix="/orgs")
addresses_router = APIRouter(prefix="/addresses")


@orgs_router.get(
    "",
    response_model=OrgsInBuildingResponse,
    **GET_ALL_ORGS,
)
async def get_all_orgs(
        request: Request,
        session: AsyncSession = Depends(get_db),
):
    org_repo = OrganizationRepository(session)

    try:
        orgs = await org_repo.list_all()
    except SQLAlchemyError as e:
        request.app.state.logger.exception("DB error while fetching organizations", exc_info=e)
        raise HTTPException(status_code=500, detail="Ошибка базы данных.")

    result = orgs_to_out(orgs)
    return {"organizations": result}


@orgs_router.get(
    "/{org_id}",
    **GET_ORG_BY_ID,
)
async def get_org_by_id(
    request: Request,
    org_id: int = Path(..., ge=1, description="Идентификатор организации"),
    session: AsyncSession = Depends(get_db),
):
    org_repo = OrganizationRepository(session)

    try:
        org = await org_repo.get_by_id(org_id)
    except SQLAlchemyError as e:
        request.app.state.logger.exception("DB error while fetching organization by id", exc_info=e)
        raise HTTPException(status_code=500, detail="Ошибка базы данных.")

    if org is None:
        raise HTTPException(status_code=404, detail="Организация не найдена.")

    return {"organization": org_to_out(org)}


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
    response_model=AddressesResponse,
    **GET_ALL_ADDRESSES,
)
async def get_all_addresses(
        request: Request,
        session: AsyncSession = Depends(get_db),
):
    address_repo = AddressRepository(session)

    try:
        addresses = await address_repo.list_all()
    except SQLAlchemyError as e:
        request.app.state.logger.exception("DB error while fetching addresses", exc_info=e)
        raise HTTPException(status_code=500, detail="Ошибка базы данных.")

    result = addresses_to_out(addresses)
    request.app.state.logger.debug(f"Result: {result}")
    return {"addresses": result}
