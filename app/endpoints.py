from app.structures import Endpoint
from datetime import datetime, timedelta
import os

BANNER_ID = os.environ["BANNER_ID"]
BANNER_GUID = os.environ["BANNER_GUID"]

ENDPOINTS: list[Endpoint] = [
    Endpoint(
        name="Persons Endpoint with BannerId Criteria",
        url="https://integrate.elluciancloud.com/api/persons",
        params={
            "criteria": {
                "credentials": [
                    {"type": "bannerId", "value": BANNER_ID}
                ]
            }
        },
        needs_bearer_token=True,
        include_response=False
    ),
    Endpoint(
        name="User Identity Profile from GUID",
        url="https://integrate.elluciancloud.com/api/user-identity-profiles",
        path_suffix=f"/{BANNER_GUID}",
        needs_bearer_token=True,
        include_response=False
    ),
    Endpoint(
        name="BEP Errors Last 7 days",
        url="https://mpc-test-bep.mpc.elluciancloud.com:8084/BannerEventPublisher/api/search-alarms",
        needs_bearer_token=False,
        include_response=True,
        needs_basic_auth=True,
        params={
            "fromDate": (datetime.now()).strftime("%m/%d/%Y %H:%M:%S"),
            "toDate": (datetime.now() - timedelta(days=7)).strftime("%m/%d/%Y %H:%M:%S")
        },
    ),
    Endpoint(
        name="BEP Single Event Status",
        url="https://mpc-prod-bep.mpc.elluciancloud.com:8084/BannerEventPublisher/api/get-event-publication-status",
        needs_bearer_token=False,
        include_response=True,
        needs_basic_auth=True,
        path_suffix="/BANROLE.APPACCEPT.SFRSTCR"
    )
]
