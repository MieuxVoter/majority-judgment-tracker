from enum import Enum, IntEnum


class Candidacy(Enum):
    """
    Select candidates
    """

    ALL_CURRENT_CANDIDATES_WITH_ENOUGH_DATA = "all_current_candidates_with_enough_data"
    ALL_CURRENT_CANDIDATES = "all_current_candidates"
    ALL_CANDIDATES_FROM_BEGINNING = "all_candidates"
    SECOND_ROUND = "second_round"
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

    ALL = "Opinion Way, ELABE, IFOP"
    MIEUX_VOTER = "Opinion Way"
    ELABE = "ELABE"
    IFOP = "IFOP"


class UntilRound(Enum):
    """
    Select which round
    """

    FIRST = "2022-04-10"
    SECOND = "2022-04-24"
