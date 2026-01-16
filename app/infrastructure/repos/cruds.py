import math
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.repos.models import *


@dataclass(slots=True)
class AddressRepository:
    session: AsyncSession

    async def get_address_id(
            self,
            /,
            country: str,
            city: str,
            street: str,
            house: int,
            building: int | None,
    ) -> int | None:
        stmt = (
            select(Address.id)
            .where(
                func.lower(Address.country) == func.lower(country),
                func.lower(Address.city) == func.lower(city),
                func.lower(Address.street) == func.lower(street),
                Address.house == house,
            )
        )

        if building is None:
            stmt = stmt.where(Address.building.is_(None))
        else:
            stmt = stmt.where(Address.building == building)

        return await self.session.scalar(stmt)

    async def list_all(self) -> list[Address]:
        stmt = select(Address).order_by(
            Address.country, Address.city, Address.street, Address.house, Address.building
        )
        return (await self.session.execute(stmt)).scalars().all()

    async def list_within_radius(
            self,
            /,
            lat: float,
            lon: float,
            radius_m: int,
            limit: int | None = None,
            offset: int | None = None,
    ) -> list[Address]:
        radius_km = radius_m / 1000.0

        km_per_deg = 111.32
        d_lat = radius_km / km_per_deg
        cos_lat = max(0.000001, math.cos(math.radians(lat)))
        d_lon = radius_km / (km_per_deg * cos_lat)

        lat_min, lat_max = lat - d_lat, lat + d_lat
        lon_min, lon_max = lon - d_lon, lon + d_lon

        lat1 = func.radians(lat)
        lon1 = func.radians(lon)
        lat2 = func.radians(Address.lat)
        lon2 = func.radians(Address.lon)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = func.pow(func.sin(dlat / 2), 2) + func.cos(lat1) * func.cos(lat2) * func.pow(func.sin(dlon / 2), 2)
        c = 2 * func.asin(func.sqrt(a))
        distance_km = 6371.0 * c

        stmt = (
            select(Address)
            .where(
                Address.lat.is_not(None),
                Address.lon.is_not(None),
                Address.lat.between(lat_min, lat_max),
                Address.lon.between(lon_min, lon_max),
                distance_km <= radius_km,
            )
            .order_by(distance_km)
        )

        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        return (await self.session.execute(stmt)).scalars().all()


@dataclass(slots=True)
class OrganizationRepository:
    session: AsyncSession

    @staticmethod
    def _load_options():
        return (
            selectinload(Organization.address),
            selectinload(Organization.phones),
            selectinload(Organization.activities),
        )

    async def list(
            self,
            /,
            address_ids: Iterable[int] | None = None,
            activity_ids: Iterable[int] | None = None,
            name: str | None = None,
            limit: int | None = None,
            offset: int | None = None,
    ) -> list[Organization]:
        stmt = (
            select(Organization)
            .options(*self._load_options())
            .order_by(Organization.name)
        )

        if address_ids:
            stmt = stmt.where(Organization.address_id.in_(list(address_ids)))

        if name is not None:
            stmt = stmt.where(Organization.name == name)

        if activity_ids:
            stmt = (
                stmt.join(Organization.activities)
                .where(Activity.id.in_(activity_ids))
                .distinct()
            )

        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        return (await self.session.execute(stmt)).scalars().all()

    async def get_by_id(self, org_id: int) -> Organization | None:
        stmt = (
            select(Organization)
            .where(Organization.id == org_id)
            .options(*self._load_options())
        )
        return await self.session.scalar(stmt)

    async def get_by_name(self, name: str) -> Organization | None:
        stmt = (
            select(Organization)
            .where(Organization.name == name)
            .options(*self._load_options())
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list("Organization"):
        return await self.list()

    async def list_by_address_id(self, address_id: int) -> list("Organization"):
        return await self.list(address_ids=[address_id])

    async def list_by_addresses_ids(self, addresses_ids: list(int)) -> list("Organization"):
        return await self.list(address_ids=addresses_ids)

    async def list_by_activities_any(self, activity_ids: int | Iterable[int]) -> list("Organization"):
        return await self.list(activity_ids=activity_ids)


@dataclass(slots=True)
class ActivityRepository:
    session: AsyncSession

    async def get_subtree_ids_by_name(self, /, name: str) -> list[int]:
        base = (
            select(Activity.id)
            .where(func.lower(Activity.name) == func.lower(name))
        )

        tree = base.cte(name="activity_tree", recursive=True)
        tree = tree.union_all(
            select(Activity.id).where(Activity.parent_id == tree.c.id)
        )

        rows = await self.session.execute(select(tree.c.id))
        return [r[0] for r in rows.all()]
