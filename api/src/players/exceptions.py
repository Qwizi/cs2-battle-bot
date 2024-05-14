from rest_framework.exceptions import ValidationError


class DiscordUserNotFound(ValidationError):
    default_code = "discord_user_not_found"
    default_detail = "DiscordUser does not exist"


class SteamUserNotFound(ValidationError):
    default_code = "steam_user_not_found"
    default_detail = "SteamUser does not exist"


class PlayerAlreadyInTeam(ValidationError):
    default_code = "player_already_in_team"
    default_detail = "Player is already in a team"


class PlayerNotInTeam(ValidationError):
    default_code = "player_not_in_team"
    default_detail = "Player is not in a team"


class PlayerNotInMatch(ValidationError):
    default_code = "player_not_in_match"
    default_detail = "Player is not in a match"


class PlayerAlreadyInMatch(ValidationError):
    default_code = "player_already_in_match"
    default_detail = "Player is already in a match"
