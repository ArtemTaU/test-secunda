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
        address_id: int | None = None,
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

        if address_id is not None:
            stmt = stmt.where(Organization.address_id == address_id)

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

    async def list_by_address(self, address_id: int) -> list("Organization"):
        return await self.list(address_id=address_id)

    async def list_by_activities_any(self, activity_ids: int | Iterable[int]) -> list("Organization"):
        return await self.list(activity_ids=activity_ids)