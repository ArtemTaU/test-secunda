from app.api.schemas import AddressOut
from app.infrastructure.repos.models import Address

def address_to_out(a: Address) -> AddressOut:
    return AddressOut.model_validate(a)

def addresses_to_out(addresses: list[Address]) -> list[AddressOut]:
    return [address_to_out(a) for a in addresses]
