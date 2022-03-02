from enum import Enum, IntEnum


class Candidacy(Enum):
    """
    Select candidates
    """

    ALL_CURRENT_CANDIDATES = "all_current_candidates"
    ALL_CANDIDATES_FROM_BEGINNING = "all_candidates"
    ALL = "all"


class AggregationMode(Enum):
    """
    Select how Aggregation are managed
    """

    NO_AGGREGATION = "None"
    FOUR_MENTIONS = "to_4_mentions"


class PollingOrganizations(Enum):
    """
    Select how Institutes
    """

    ALL = "None"
    MIEUX_VOTER = "Mieux voter"
