from libs.majority_judgment_2 import majority_judgment as mj
import numpy as np
import pandas as pd
from pandas import DataFrame
from utils import get_intentions, get_grades, get_list_survey


def apply_mj(
    df: DataFrame,
):
    """
    Reindexing candidates in the dataFrame following majority judgment rules

    Parameters
    ----------
    df: DataFrame
        contains all the data of vote / survey
    Returns
    -------
    Return the DataFrame df with the rank within majority judgment rules for all studies
    """

    # Compute the rank for each survey
    df["rang"] = None
    df["mention_majoritaire"] = None

    surveys = get_list_survey(df)

    for survey in surveys:
        print(survey)
        # only the chosen survey
        df_survey = df[df["id"] == survey].copy()

        nb_grades = df_survey["nombre_mentions"].unique()[0]

        df_with_rank = sort_candidates_mj(df_survey, nb_grades)

        # refill the dataframe of surveys
        df[df["id"] == survey] = df_with_rank

    return df


def sort_candidates_mj(
    df: DataFrame,
    nb_grades: int,
):
    """
    Reindexing candidates in the dataFrame following majority judgment rules

    Parameters
    ----------
    df: DataFrame
        contains all the data of vote / survey
    nb_grades: int
        number of grades
    Returns
    -------
    Return the DataFrame df sorted with the rank within majority judgment rules.
    """
    nb_candidates = len(df)

    df_intentions = get_intentions(df, nb_grades)

    merit_profiles_dict = set_dictionary(df_intentions, nb_grades, nb_candidates)
    ranking, best_grades = mj(merit_profiles_dict, reverse=True)

    if "rang" not in df.columns:
        df["rang"] = None
    if "mention_majoritaire" not in df.columns:
        df["mention_majoritaire"] = None

    col_rank = df.columns.get_loc("rang")
    col_best_grade = df.columns.get_loc("mention_majoritaire")
    for c in ranking:
        idx = np.where(df["candidat"] == c)[0][0]
        df.iat[idx, col_rank] = ranking[c]

    grade_list = get_grades(df)
    grade_list.reverse()
    for c in best_grades:
        idx = np.where(df["candidat"] == c)[0][0]
        df.iat[idx, col_best_grade] = grade_list[best_grades[c]]

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
