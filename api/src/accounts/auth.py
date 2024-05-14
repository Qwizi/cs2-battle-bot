from django.conf import settings
from django.urls import reverse
import httpx
from rest_framework.authentication import TokenAuthentication
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import KeyParser, BaseHasAPIKey

from accounts.schemas import SteamAuthSchema
from steam.webapi import WebAPI
from steam.steamid import SteamID


class SteamAuthService:
    """
    Service class for handling Steam authentication.

    Attributes
    ----------
        users_service (UserService): The user service.
        players_service (PlayerService): The player service.
        auth_url (str): The Steam authentication URL.

    Methods
    -------
        get_steamid_from_url: Get the Steam ID from a Steam profile URL.
        format_params: Format the Steam authentication parameters into a dict.
        is_valid_params: Check if the provided Steam authentication parameters are valid.
        authenticate: Authenticate a user using Steam authentication.
    """

    def __init__(
        self,
    ) -> None:
        """Initialize the SteamAuthService."""
        self.auth_url = "https://steamcommunity.com/openid/login"

    def get_login_url(self, request):
        steam_callback_relative_url = reverse("steam_callback")
        steam_callback_full_url = request.build_absolute_uri(
            steam_callback_relative_url
        )
        openid_realm = request.build_absolute_uri()
        #  remove from url /accounts/steam/
        openid_realm = openid_realm[:-15]
        return (
            f""
            f"{self.auth_url}?openid.ns=http://specs.openid.net/auth/2.0"
            f"&openid.identity=http://specs.openid.net/auth/2.0/identifier_select"
            f"&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select"
            f"&openid.mode=checkid_setup"
            f"&openid.return_to={steam_callback_full_url}"
            f"&openid.realm={openid_realm}"
        )

    @staticmethod
    def get_steamid_from_url(url: str) -> str:
        """
        Extracts the SteamID from a given Steam profile URL.

        Args:
        ----
            url (str): The Steam profile URL.

        Returns:
        -------
            str: The extracted SteamID.
        """  # noqa: D401
        return url.split("/")[-1]

    def format_params(self, params: SteamAuthSchema) -> dict:
        """
        Format the Steam authentication parameters into a dict.

        Args:
        ----
            params (SteamAuthSchema): The Steam authentication parameters.

        Returns:
        -------
            dict: The formatted parameters.
        """
        params_dict = {}
        params_dict["openid.ns"] = params.openid_ns
        params_dict["openid.mode"] = params.openid_mode
        params_dict["openid.op_endpoint"] = params.openid_op_endpoint
        params_dict["openid.claimed_id"] = params.openid_claimed_id
        params_dict["openid.identity"] = params.openid_identity
        params_dict["openid.return_to"] = params.openid_return_to
        params_dict["openid.response_nonce"] = params.openid_response_nonce
        params_dict["openid.assoc_handle"] = params.openid_assoc_handle
        params_dict["openid.signed"] = params.openid_signed
        params_dict["openid.sig"] = params.openid_sig
        return params_dict

    def is_valid_params(self, params: SteamAuthSchema) -> bool:
        """
        Check if the provided Steam authentication parameters are valid.

        Args:
        ----
            params (SteamAuthSchema): The Steam authentication parameters.

        Returns:
        -------
            bool: True if the parameters are valid, False otherwise.
        """
        params_copy = params
        params_copy.openid_mode = "check_authentication"
        formatted_params = self.format_params(params_copy)
        with httpx.Client() as client:
            response = client.post(url=self.auth_url, data=formatted_params)
            return "is_valid:true" in response.text

    def get_player_info(self, steamid64) -> dict:
        steam_api = WebAPI(settings.STEAM_API_KEY)
        results = steam_api.call(
            "ISteamUser.GetPlayerSummaries",
            steamids=steamid64,
        )
        if not len(results["response"]["players"]):
            msg = "Invalid steamid64"
            raise Exception(msg)  # noqa: TRY002

        player = results["response"]["players"][0]

        profile_url = player["profileurl"]
        avatar = player["avatarfull"]

        steamid64_from_player = player["steamid"]
        steamid32 = SteamID(steamid64_from_player).as_steam2
        return {
            "username": player["personaname"],  # noqa: TRY002
            "steamid64": steamid64_from_player,
            "steamid32": steamid32,
            "profile_url": profile_url,
            "avatar": avatar,
        }

    def authenticate(self, user: dict, params: SteamAuthSchema):
        """
        Authenticate a user using Steam authentication.

        Args:
        ----
            user (User): The user to authenticate.
            params (SteamAuthSchema): The Steam authentication parameters.

        Returns:
        -------
            Player: The authenticated player.

        Raises:
        ------
            HTTPException: If the Steam profile cannot be authenticated or if the user is already connected to a profile.
        """
        if not self.is_valid_params(params):
            raise Exception(400, "Cannot authenticate steam profile")
        return self.get_steamid_from_url(params.openid_claimed_id)


class DiscordAuthService:
    """
    Service class for handling Discord authentication.

    Attributes
    ----------
        auth_url (str): The Discord authentication URL.

    Methods
    -------
        get_login_url: Get the Discord authentication URL.
        exchange_code: Exchange a code for an access token.
        get_user_info: Get the user information from the access token.
    """

    def __init__(self) -> None:
        """Initialize the DiscordAuthService."""
        self.auth_url = "https://discord.com/api/oauth2/authorize"
        self.token_url = "https://discord.com/api/oauth2/token"

    def get_login_url(self, request):
        redirect_url = request.build_absolute_uri(reverse("discord_callback"))
        print(redirect_url)
        return (
            f""
            f"{self.auth_url}?client_id={settings.DISCORD_CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={redirect_url}"
            f"&scope=identify+email"
        )

    def exchange_code(self, code: str, request) -> dict:
        """
        Exchange a code for an access token.

        Args:
        ----
            code (str): The code to exchange.

        Returns:
        -------
            dict: The access token.
        """
        redirect_url = request.build_absolute_uri(reverse("discord_callback"))
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_url,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        with httpx.Client() as client:
            response = client.post(
                url=self.token_url,
                data=data,
                headers=headers,
                auth=(settings.DISCORD_CLIENT_ID, settings.DISCORD_CLIENT_SECRET),
            )
            response.raise_for_status()
            return response.json()

    def get_user_info(self, access_token: str) -> dict:
        """
        Get the user information from the access token.

        Args:
        ----
            access_token (str): The access token.

        Returns:
        -------
            dict: The user information.
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        with httpx.Client() as client:
            response = client.get(
                url="https://discord.com/api/users/@me", headers=headers
            )
            return response.json()


class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"


class BearerKeyParser(KeyParser):
    keyword = "Bearer"


class HasAPIKey(BaseHasAPIKey):
    model = APIKey  # Or a custom model
    key_parser = BearerKeyParser()
