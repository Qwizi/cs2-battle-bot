from dataclasses import dataclass


@dataclass
class SteamAuthSchema:
    """Schema for the steam auth."""

    openid_ns: str
    openid_mode: str
    openid_op_endpoint: str
    openid_claimed_id: str
    openid_identity: str
    openid_return_to: str
    openid_response_nonce: str
    openid_assoc_handle: str
    openid_signed: str
    openid_sig: str
