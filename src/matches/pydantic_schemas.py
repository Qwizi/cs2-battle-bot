import typing
from enum import Enum

import pydantic


class SideChoice(Enum):
    TEAM1_CT = "team1_ct"
    TEAM2_CT = "team2_ct"
    TEAM1_T = "team1_t"
    TEAM2_T = "team2_t"
    KNIFE = "knife"


class MapBan(pydantic.BaseModel):
    tag: str
    name: str

class MapList(MapBan):
    pass

class MatchConfigTeamJSON(pydantic.BaseModel):
    name: str
    players: typing.Dict[str, str]


class MatchConfigSpecJSON(pydantic.BaseModel):
    players: typing.Dict[str, str]

class MatchConfigJSON(pydantic.BaseModel):
    match_id: int
    team1: MatchConfigTeamJSON
    team2: MatchConfigTeamJSON
    num_maps: int
    maplist: typing.List[str]
    map_sides: typing.List[SideChoice]
    spectators: MatchConfigSpecJSON
    clinch_series: bool
    players_per_team: int
    cvars: typing.Dict[str, str]