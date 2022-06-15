from enum import Enum


class AgentType(Enum):
    """
    Category of community member.
    """
    CONSUMER = 1
    PROSUMER = 2
    COORDINATOR = 3
    ASSET = 4


class MemberType(Enum):
    """
    Type of community member.
    """
    RESIDENTIAL = 1
    NON_RESIDENTIAL = 2
    COORDINATOR = 3


class AssetType(Enum):
    """
    Type of asset.
    """
    SOLAR = 1
    WIND = 2
    BATTERY_STORAGE = 3
