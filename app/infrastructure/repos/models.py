from typing import Optional, List
from sqlalchemy import Integer, Text, ForeignKey, UniqueConstraint, Index
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

    organizations: Mapped[List["Organization"]] = relationship(
        back_populates="address",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "country", "city", "street", "house", "building",
            name="uq_addresses_full"
        ),
        Index("ix_addresses_lookup", "country", "city", "street", "house"),
    )
