from app.api.schemas import OrganizationOut, AddressOut
from app.infrastructure.repos.models import Organization


def org_to_out(o: Organization) -> OrganizationOut:
    return OrganizationOut(
        id=o.id,
        name=o.name,
        address=AddressOut.model_validate(o.address),
        phones=[p.phone for p in o.phones],
        activities=[a.name for a in o.activities],
    )


def orgs_to_out(orgs: list[Organization]) -> list[OrganizationOut]:
    return [org_to_out(o) for o in orgs]
