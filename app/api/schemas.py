from pydantic import BaseModel, Field, ConfigDict


class BuildingAddressQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    country: str = Field(..., min_length=1, max_length=20, examples=["Россия"])
    city: str = Field(..., min_length=1, max_length=20, examples=["Москва"])
    street: str = Field(..., min_length=1, max_length=20, examples=["Тверская"])
    house: int = Field(..., ge=1, le=1000, examples=[1])
    building: int | None = Field(None, ge=1, examples=[2])


class AddressOut(BaseModel):
    id: int
    country: str
    city: str
    street: str
    house: int
    building: int | None = None
    lat: float | None = None
    lon: float | None = None

    class Config:
        from_attributes = True


class OrganizationOut(BaseModel):
    id: int
    name: str
    address: AddressOut
    phones: list[str]
    activities: list[str]


class OrgsInBuildingResponse(BaseModel):
    organizations: list[OrganizationOut]


class AddressesResponse(BaseModel):
    addresses: list[AddressOut]


class AddressesWithOrganizationsResponse(BaseModel):
    addresses: list[AddressOut]
    organizations: list[OrganizationOut]
