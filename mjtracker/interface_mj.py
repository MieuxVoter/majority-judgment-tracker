from typing import List
from operator import itemgetter

import numpy as np
from pandas import DataFrame
from mjtracker.utils import get_grades, get_list_survey
from .libs.majority_judgment_2 import majority_judgment as mj
# from .libs.majority_judgment import majority_judgment as mj


def interface_to_official_lib(merit_profiles_dict: dict, reverse: bool):
    """ source: https://github.com/MieuxVoter/majority-judgment-library-python/tree/main """
    from majority_judgment import majority_judgment as mj
    from majority_judgment import compute_majority_values
    from majority_judgment import median_grade
    official_merit_profiles_dict = dict()
    for k, v in merit_profiles_dict.items():
        official_merit_profiles_dict[k] = [[i] * x for i, x in enumerate(v)]
        official_merit_profiles_dict[k] = [item for sublist in official_merit_profiles_dict[k] for item in sublist]

    set_num_votes = {len(votes) for votes in official_merit_profiles_dict.values()}
    if not len(set_num_votes) == 1:
        raise NotImplementedError("Unbalanced grades have not been implemented yet.")

    best_grades = {}
    for candidate, votes in merit_profiles_dict.items():
        best_grades[candidate] = median_grade(np.cumsum(votes)/np.sum(votes))

    return mj(official_merit_profiles_dict, reverse=reverse), best_grades


def apply_mj(
    df: DataFrame,
    rolling_mj: bool = False,
    official_lib: bool = False,
    reversed: bool = True,
):
    """
    Reindexing candidates in the dataFrame following majority judgment rules

    Parameters
    ----------
    df: DataFrame
        contains all the data of vote / survey
    rolling_mj: bool
        if we apply rolling majority judgment
    official_lib: bool
        if we use the official majority judgment lib from MieuxVoter
    Returns
    -------
    Return the DataFrame df with the rank within majority judgment rules for all studies
    """
    surveys = get_list_survey(df)
    # Compute the rank for each survey
    col_rank = "rang_glissant" if rolling_mj else "rang"
    col_median_grade = "mention_majoritaire_glissante" if rolling_mj else "mention_majoritaire"
    df[col_rank] = None
    df[col_median_grade] = None

    suffix = "_roll" if rolling_mj else ""
    col_intentions = [f"intention_mention_{i}{suffix}" for i in range(1, 8)]

    for survey in surveys:
        print(survey)
        # only the chosen survey
        df_survey = df[df["id"] == survey].copy()
        nb_grades = int(df_survey["nombre_mentions"].unique()[0])
        cur_col_intentions = col_intentions[:nb_grades]
        df_with_rank = sort_candidates_mj(
            df_survey,
            nb_grades,
            col_rank,
            col_median_grade,
            cur_col_intentions,
            official_lib,
            reversed,
        )
        # refill the dataframe of surveys
        df[df["id"] == survey] = df_with_rank

    return df


def sort_candidates_mj(
    df: DataFrame,
    nb_grades: int,
    col_rank: str = None,
    col_median_grade: str = None,
    col_intentions: List[str] = None,
    official_lib: bool = False,
    reversed: bool = True,
):
    """
    Reindexing candidates in the dataFrame following majority judgment rules

    Parameters
    ----------
    df: DataFrame
        contains all the data of vote / survey
    nb_grades: int
        number of grades
    col_rank: str
        rank col to considered (ex: rang or rang_glissant)
    col_median_grade: str
        rank col to considered (ex: mention_majoritaire or mention_majoritaire_glissante)
    col_intentions: list[str]
        col of intentions to considered (ex: _roll or not)
    official_lib: bool
        if we use the official majority judgment lib from MieuxVoter
    Returns
    -------
    Return the DataFrame df sorted with the rank within majority judgment rules.
    """
    col_rank = "rang" if col_rank is None else col_rank
    col_median_grade = "mention_majoritaire" if col_median_grade is None else col_median_grade

    nb_candidates = len(df)
    # todo: get the df with this intention_col
    # df_intentions = get_intentions(df, nb_grades)
    colheader = ["candidat"]
    colheader.extend(col_intentions)
    df_intentions = df[colheader]
    merit_profiles_dict = set_dictionary(df_intentions, nb_grades, nb_candidates)
    # ranking, best_grades = mj(merit_profiles_dict, reverse=True)

    if official_lib:
        ranking, best_grades = interface_to_official_lib(merit_profiles_dict, reverse=reversed)
    else:
        # for majority-judgment-tracker has I kept percentages instead of votes, this method is preferred
        ranking, best_grades = mj(merit_profiles_dict, reverse=reversed)

    if col_rank not in df.columns:
        df[col_rank] = None
    if col_median_grade not in df.columns:
        df[col_median_grade] = None

    col_rank = df.columns.get_loc(col_rank)
    col_best_grade = df.columns.get_loc(col_median_grade)
    for c in ranking:
        idx = np.where(df["candidat"] == c)[0][0]
        df.iat[idx, col_rank] = ranking[c]

    grade_list = get_grades(df)
    if not reversed:
        grade_list.reverse()

    for c, val in best_grades.items():
        print(c, grade_list[val])
        idx = np.where(df["candidat"] == c)[0][0]
        df.iat[idx, col_best_grade] = grade_list[val]

    return df


def set_dictionary(df_intentions: DataFrame, nb_grades: int, nb_candidates: int):
    """
    Convert a DataFrame of votes into a dictionary Dict[str, list] containing the number of grades for
    each candidate

    Parameters
    ----------
    df_intentions: DataFrame
        contains only all votes for each grade
    nb_grades: int
        number of grades
    nb_candidates: int,
        number of candidates
    Returns
    -------
    a dictionary Dict[str, list] containing the number of grades for
    each candidate
    """
    return {
        df_intentions["candidat"].iloc[i]: [df_intentions.iloc[i, j + 1] for j in range(nb_grades)]
        for i in range(nb_candidates)
    }
