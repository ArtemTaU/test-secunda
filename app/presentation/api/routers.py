from typing import Optional

from fastapi import APIRouter, Query, Request, Depends

from .openapi import CHECK_ORGS_IN_BUILDING
from ...domain.schemas import OrgsInBuildingResponse, BuildingAddressQuery

orgs_router = APIRouter(prefix="/orgs")


@orgs_router.get("/address", response_model=OrgsInBuildingResponse, **CHECK_ORGS_IN_BUILDING)
async def check_orgs_in_building(
    request: Request,
    q: BuildingAddressQuery = Depends(),
):
    return {"organizations": []}