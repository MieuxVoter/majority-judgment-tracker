from libs.majority_judgment_2 import majority_judgment as mj
import pandas as pd
from pandas import DataFrame
from utils import (
    get_intentions,
    get_intentions_colheaders,
)


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

    col = get_intentions_colheaders(df, nb_grades)

    # only intentions of votes in the dataframe
    intentions = df[col]

    # merit_profiles1 = set_merit_profiles(intentions, nb_grades, nb_candidates)
    # merit_profiles2 = set_merit_profiles2(intentions, nb_grades, nb_candidates)
    # merit_profiles3 = set_merit_profiles3(intentions, nb_grades, nb_candidates)

    # # generate data for the use of mj
    # majo_vals = [mj.MajorityValue(profil) for profil in merit_profiles1]
    # sorted_majo_vals = mj.sort_by_value_with_index(majo_vals)
    # get back index of ranks for each candidates
    # rank_idx = [idx for idx, value in sorted_majo_vals]
    # rank_idx.reverse()

    merit_profiles_dict = set_dictionary(df_intentions, nb_grades, nb_candidates)
    ranking = mj(merit_profiles_dict, reverse=True)

    # copy and empy the panda datafram to refill it.
    new_df = df_intentions.copy()
    new_df = new_df.drop(
        labels=new_df.index, axis=0, index=None, columns=None, level=None, inplace=True, errors="raise"
    )
    # refilling the dataframe
    for key in ranking:
        row = df_intentions[df_intentions["candidat"] == key]
        new_df = pd.concat([new_df, row], ignore_index=True)
    # set new index of rows
    new_df.index = pd.Index(data=[i for i in range(1, nb_candidates + 1)], dtype="int64")

    return new_df.reindex(index=new_df.index[::-1])  # sort to plot it the right way, best candidate at the top.


def set_merit_profiles(df_intentions: DataFrame, nb_grades: int, nb_candidates: int):
    """
    Convert a list of votes into a matrix containing the number of grades for
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
    A list of dictionaries which contains the number of votes for each grade for each candidates,
    the length of the list is the number of candidates
    """
    return [{j: df_intentions.iloc[i, j] for j in range(nb_grades)} for i in range(nb_candidates)]


def set_merit_profiles2(df_intentions: DataFrame, nb_grades: int, nb_candidates: int):
    """
    Convert a list of votes into a matrix containing the number of grades for
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
    A list of dictionaries which contains the number of votes for each grade for each candidates,
    the length of the list is the number of candidates
    """
    return [
        {j: df_intentions.iloc[i, nb_grades - j - 1] for j in range(nb_grades - 1, -1, -1)}
        for i in range(nb_candidates)
    ]


def set_dictionary(df_intentions: DataFrame, nb_grades: int, nb_candidates: int):
    """
    Convert a list of votes into a matrix containing the number of grades for
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
    A list of dictionaries which contains the number of votes for each grade for each candidates,
    the length of the list is the number of candidates
    """
    return {
        df_intentions["candidat"].iloc[i]: [df_intentions.iloc[i, j + 1] for j in range(nb_grades)]
        for i in range(nb_candidates)
    }
