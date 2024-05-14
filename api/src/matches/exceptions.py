from rest_framework.exceptions import ValidationError


class ConfigNotFound(ValidationError):
    default_code = "config_not_found"


class InvalidMatchStatus(ValidationError):
    default_code = "invalid_match_status"
    default_detail = "Match status is invalid"
