from typing import Optional, List
from sqlalchemy import Integer, Text, ForeignKey, UniqueConstraint, Index, Float, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    country: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    street: Mapped[str] = mapped_column(Text, nullable=False)

    house: Mapped[int] = mapped_column(Integer, nullable=False)
    building: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    organizations: Mapped[List["Organization"]] = relationship(
        back_populates="address",
    )

    __table_args__ = (
        UniqueConstraint(
            "country", "city", "street", "house", "building",
            name="uq_addresses_full"
        ),
        Index("ix_addresses_lookup", "country", "city", "street", "house"),
        Index("ix_addresses_geo", "lat", "lon"),
    )


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    parent: Mapped[Optional["Activity"]] = relationship(
        "Activity",
        back_populates="children",
        remote_side="Activity.id",
    )

    children: Mapped[List["Activity"]] = relationship(
        "Activity",
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Activity.name",
    )

    organizations: Mapped[List["Organization"]] = relationship(
        secondary=lambda: organization_activities,
        back_populates="activities",
    )

    __table_args__ = (
        UniqueConstraint("parent_id", "name", name="uq_activity_parent_name"),
        Index("ix_activity_parent_name", "parent_id", "name"),
    )


organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column(
        "organization_id",
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Column(
        "activity_id",
        ForeignKey(
        "activities.id",
               ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Index("ix_org_act_activity", "activity_id"),
)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    address_id: Mapped[int] = mapped_column(
        ForeignKey("addresses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    address: Mapped["Address"] = relationship(
        "Address",
        back_populates="organizations",
    )

    phones: Mapped[List["OrganizationPhone"]] = relationship(
        "OrganizationPhone",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="OrganizationPhone.phone",
    )

    activities: Mapped[List["Activity"]] = relationship(
        "Activity",
        secondary=organization_activities,
        back_populates="organizations",
        order_by="Activity.name",
    )

    __table_args__ = (
        Index("ix_org_name", "name"),
    )



class OrganizationPhone(Base):
    __tablename__ = "organization_phones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    phone: Mapped[str] = mapped_column(Text, nullable=False)

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="phones",
    )

    __table_args__ = (
        UniqueConstraint("organization_id", "phone", name="uq_org_phone"),
        Index("ix_org_phone_phone", "phone"),
    )


__all__ = [
    "Organization",
    "OrganizationPhone",
    "Activity",
    "Address",
]