from enum import Enum


class MemberType(Enum):
    """
    Type of community member_name.
    """
    CONSUMER = 1
    PROSUMER = 2
    COORDINATOR = 3
    ASSET = 4


class AssetType(Enum):
    """
    Type of asset.
    """
    SOLAR = 1
    WIND = 2
    BATTERY_STORAGE = 3
