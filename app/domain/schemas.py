from pydantic import BaseModel, Field, ConfigDict


class BuildingAddressQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    country: str = Field(..., min_length=1, max_length=20)
    city: str = Field(..., min_length=1, max_length=20)
    street: str = Field(..., min_length=1, max_length=20)
    house: int = Field(..., ge=1, le=1000)
    building: int | None = Field(None, ge=1)


class OrgsInBuildingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organizations: list[str]