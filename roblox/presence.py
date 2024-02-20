"""

This module contains classes intended to parse and deal with data from Roblox presence endpoints.

"""

from __future__ import annotations

from datetime import datetime
from enum import IntEnum
from typing import Optional, List
from typing import TYPE_CHECKING

from dateutil.parser import parse

from .bases.basejob import BaseJob
from .bases.baseplace import BasePlace
from .bases.baseuniverse import BaseUniverse

if TYPE_CHECKING:
    from .client import Client
    from .bases.baseuser import BaseUser
    from .utilities.types import UserOrUserId


class PresenceType(IntEnum):
    """
    Represents a user's presence type.
    """
    offline = 0
    online = 1
    in_game = 2
    in_studio = 3


class Presence:
    """
    Represents a user's presence.

    Attributes:
        user_presence_type: The type of the presence.
        last_location: A string representing the user's last location.
        place: The place the user is playing or editing.
        root_place: The root place of the parent universe of the last place the user is playing or editing.
        job: The job of the root place that the user is playing or editing.
        universe: The universe the user is playing or editing.
        last_online: When the user was last online.
        user: The user this presence belongs to.
    """

    def __init__(self, client: Client, data: dict):
        """
        Arguments:
            client: Client object.
            data: The data from the request.
        """
        self._client: Client = client

        self.user_presence_type: PresenceType = PresenceType(data["userPresenceType"])
        self.last_location: str = data["lastLocation"]

        self.place: Optional[BasePlace] = BasePlace(
            client=client,
            place_id=data["placeId"]
        ) if data.get("placeId") else None

        self.root_place: Optional[BasePlace] = BasePlace(
            client=client,
            place_id=data["rootPlaceId"]
        ) if data.get("rootPlaceId") else None

        self.job: Optional[BaseJob] = BaseJob(self._client, data["gameId"]) if data.get("gameId") else None

        self.universe: Optional[BaseUniverse] = BaseUniverse(
            client=client,
            universe_id=data["universeId"]
        ) if data.get("universeId") else None

        self.user: BaseUser = client.get_base_user(data["userId"])
        self.last_online: datetime = parse(data["lastOnline"])

    def __repr__(self):
        return f"<{self.__class__.__name__} user_presence_type={self.user_presence_type}>"


class PresenceProvider:
    """
    The PresenceProvider is an object that represents https://presence.roblox.com/ and provides multiple functions
    for fetching user presence information.
    """

    def __init__(self, client: Client):
        self._client: Client = client

    async def get_user_presences(self, users: List[UserOrUserId]) -> List[Presence]:
        """
        Grabs a list of Presence objects corresponding to each user in the list.

        Arguments:
            users: The list of users you want to get Presences from.

        Returns:
            A list of Presences.
        """

        presences_response = await self._client.requests.post(
            url=self._client.url_generator.get_url("presence", "v1/presence/users"),
            json={
                "userIds": list(map(int, users))
            }
        )
        presences_data = presences_response.json()["userPresences"]
        return [Presence(client=self._client, data=presence_data) for presence_data in presences_data]
