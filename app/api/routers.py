from fastapi import APIRouter, Request, Depends, HTTPException, Path, Query

from app.infrastructure.dependencies import get_db
from .mappers.addresses import addresses_to_out
from .mappers.organizations import orgs_to_out, org_to_out
from .openapi import CHECK_ORGS_IN_BUILDING, GET_ALL_ORGS, GET_ALL_ADDRESSES, GET_ORG_BY_ID, \
    GET_ADDRESSES_AND_COMPANIES_NEAR, GET_ORGS_BY_ACTIVITY_TREE
from app.api.schemas import (
    OrgsInBuildingResponse,
    BuildingAddressQuery,
    AddressesResponse,
    AddressesWithOrganizationsResponse,
)
from app.infrastructure.repos.cruds import AddressRepository, OrganizationRepository, ActivityRepository

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
    "/activity",
    response_model=OrgsInBuildingResponse,
    **GET_ORGS_BY_ACTIVITY_TREE,
)
async def get_orgs_by_activity_tree(
        request: Request,
        activity: str = Query(..., min_length=1, description="Название вида деятельности (например: Еда)"),
        session: AsyncSession = Depends(get_db),
):
    activity_repo = ActivityRepository(session)
    org_repo = OrganizationRepository(session)

    try:
        activity_ids = await activity_repo.get_subtree_ids_by_name(activity.strip())
    except SQLAlchemyError as e:
        request.app.state.logger.exception("DB error while fetching activity subtree", exc_info=e)
        raise HTTPException(status_code=500, detail="Ошибка базы данных.")

    if not activity_ids:
        raise HTTPException(status_code=404, detail="Вид деятельности не найден.")

    try:
        orgs = await org_repo.list_by_activities_any(activity_ids)
    except SQLAlchemyError as e:
        request.app.state.logger.exception("DB error while fetching organizations by activities", exc_info=e)
        raise HTTPException(status_code=500, detail="Ошибка базы данных.")

    return {"organizations": orgs_to_out(orgs)}


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

    try:
        address_id = await address_repo.get_address_id(
            country=country,
            city=city,
            street=street,
            house=house,
            building=building,
        )
    except SQLAlchemyError as e:
        request.app.state.logger.exception("DB error while fetching address_id", exc_info=e)
        raise HTTPException(status_code=500, detail="Ошибка базы данных.")

    if address_id is None:
        raise HTTPException(status_code=404, detail="Здание не найдено.")

    try:
        orgs = await org_repo.list_by_address_id(address_id)
    except SQLAlchemyError as e:
        request.app.state.logger.exception("DB error while fetching organizations by address", exc_info=e)
        raise HTTPException(status_code=500, detail="Ошибка базы данных.")

    return {"organizations": orgs_to_out(orgs)}


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


@addresses_router.get(
    "/near",
    response_model=AddressesWithOrganizationsResponse,
    **GET_ADDRESSES_AND_COMPANIES_NEAR,
)
async def get_addresses_near(
        request: Request,
        lat: float = Query(..., ge=-90, le=90, description="Широта точки"),
        lon: float = Query(..., ge=-180, le=180, description="Долгота точки"),
        radius_m: int = Query(1000, gt=0, le=100_0000, description="Радиус поиска в метрах"),
        limit: int | None = Query(None, gt=0, le=1000),
        offset: int | None = Query(None, ge=0),
        session: AsyncSession = Depends(get_db),
):
    address_repo = AddressRepository(session)
    org_repo = OrganizationRepository(session)

    try:
        addresses = await address_repo.list_within_radius(lat, lon, radius_m, limit=limit, offset=offset)
        address_ids = [a.id for a in addresses]
        orgs = await org_repo.list_by_addresses_ids(address_ids)
    except SQLAlchemyError as e:
        request.app.state.logger.exception("DB error while fetching addresses/orgs near point", exc_info=e)
        raise HTTPException(status_code=500, detail="Ошибка базы данных.")

    return {
        "addresses": addresses_to_out(addresses),
        "organizations": orgs_to_out(orgs),
    }
