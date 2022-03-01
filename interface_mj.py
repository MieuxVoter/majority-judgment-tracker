from libs.majority_judgment_2 import majority_judgment as mj
import numpy as np
import pandas as pd
from pandas import DataFrame
from utils import get_intentions


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
    ranking = mj(merit_profiles_dict, reverse=True)

    if "rang" not in df.columns:
        df["rang"] = None

    col_index = df.columns.get_loc("rang")
    for c in ranking:
        idx = np.where(df["candidat"] == c)[0][0]
        df.iat[idx, col_index] = ranking[c]

    # # copy and empty the panda datafram to refill it.
    # new_df = df_intentions.copy()
    # new_df = new_df.drop(
    #     labels=new_df.index, axis=0, index=None, columns=None, level=None, inplace=True, errors="raise"
    # )
    # # refilling the dataframe
    # for key in ranking:
    #     row = df_intentions[df_intentions["candidat"] == key]
    #     new_df = pd.concat([new_df, row], ignore_index=True)
    # # set new index of rows
    # new_df.index = pd.Index(data=[i for i in range(1, nb_candidates + 1)], dtype="int64")
    # return new_df.reindex(index=new_df.index[::-1]) # sort to plot it the right way, best candidate at the top.

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
