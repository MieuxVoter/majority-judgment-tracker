#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 15:10:01 2022

@author: sballe
"""
from pathlib import Path
import pandas as pd
from pandas import DataFrame
import numpy as np
import sqlite3
import os

from utils import get_list_survey

from misc.enums import Candidacy, AggregationMode, PollingOrganizations


def remove_undecided(df_survey: DataFrame, df_undecided_grades: DataFrame):
    """
    Remove the undecided grades and affect it proportionally to the other grades

    Parameters
    ----------
    df_survey: DataFrame
        dataframe of the survey
    df_undecided_grades: DataFrame
        corresponding grade which value no opinion
    Returns
    -------
        return the DataFrame df with the survey with reaffected no opinion to the other grades
    """
    # compute initial number of grades attributed to each candidates
    cols = [f"intention_mention_{i + 1}" for i in range(df_survey["nombre_mentions"].iloc[0])]
    tot = df_survey[cols].sum(axis=1).unique()
    if len(tot) != 1:
        id_survey = df_survey["id"][df_survey.first_valid_index()]
        raise ValueError(f"the number of grades is not equal for each candidate in {id_survey}")

    tot = tot[0]

    # find the undecided grade
    cols_grades = [f"mention_{i + 1}" for i in range(df_survey["nombre_mentions"].iloc[0])]
    the_undecided_grades = []
    the_undecided_grade_nums = []
    for undecided_grade in df_undecided_grades["mention"]:
        bool_with_undecided = df_survey[cols_grades].iloc[0, :].str.contains(undecided_grade)
        if bool_with_undecided.any():
            the_undecided_grades.append(bool_with_undecided[bool_with_undecided].index)
            the_undecided_grade_nums.append(np.where(bool_with_undecided)[0][0])

    # remove the undecided grades
    if the_undecided_grade_nums:
        for ii in the_undecided_grades:
            df_survey.loc[df_survey.index, ii] = "nan"

        index_no = df_survey.columns.get_loc("nombre_mentions")
        df_survey.loc[df_survey.index, "nombre_mentions"] = int(df_survey.iloc[0, index_no] - len(the_undecided_grades))

        cols_grades_undecided = [f"intention_mention_{i + 1}" for i in the_undecided_grade_nums]
        cols_grades_decided = [
            f"intention_mention_{i + 1}"
            for i in range(df_survey["nombre_mentions"].iloc[0])
            if f"intention_mention_{i + 1}" not in cols_grades_undecided
        ]

        tot_undecided = df_survey[cols_grades_undecided].sum(axis=1)
        tot_decided = df_survey[cols_grades_decided].sum(axis=1)

        for col_grade_decided in cols_grades_decided:
            index_no = df_survey.columns.get_loc(col_grade_decided)
            df_survey.iloc[:, index_no] = df_survey.iloc[:, index_no] * (1 + tot_undecided / tot_decided)

        # the no opinion col to zero and store it somwehere else
        df_survey["sans_opinion"] = df_survey[cols_grades_undecided].sum(axis=1)
        df_survey[cols_grades_undecided] = 0


        if np.round(df_survey[cols_grades_decided].sum(axis=1) - tot, 10).any() != 0:
            raise ValueError("Something went wrong when reaffecting undecided grades.")

    return df_survey


def convert_grades(
    df_survey: DataFrame, df_corresponding_grades: DataFrame, aggregation: AggregationMode, no_opinion_mode: bool
):
    """
    Remove the undecided grades and affect it proportionally to the other grades

    Parameters
    ----------
    df_survey: DataFrame
        dataframe of the survey
    df_corresponding_grades: DataFrame
        corresponding grade (ex: Excellent and good to very positive)
    aggregation: AggregationMode
        how to manage Aggregation of several grades
    no_opinion_mode: bool
        remove or not the undecided grades
    Returns
    -------
        return the DataFrame df with the survey with affected new grades and new intentions
    """
    # remove no opinion of the aggregate if already removed
    col = aggregation.value
    if no_opinion_mode:
        df_corresponding_grades = df_corresponding_grades[df_corresponding_grades[col] != "sans opinion"]

    # grades of the current survey
    cols_grades = [f"mention_{i + 1}" for i in range(df_survey["nombre_mentions"].iloc[0])]
    cols_grades_idx = [df_survey.columns.get_loc(c) for c in cols_grades]

    cols_intentions = [f"intention_mention_{i + 1}" for i in range(df_survey["nombre_mentions"].iloc[0])]
    cols_intentions_idx = [df_survey.columns.get_loc(c) for c in cols_intentions]
    grades_survey = df_survey[cols_grades].loc[df_survey.first_valid_index()]

    # loop over the objectives new grades to replace the older ones
    new_grades = df_corresponding_grades[col].unique()

    # Refill the new_survey dataframe
    new_df_survey = df_survey.copy()
    new_df_survey.iloc[:, cols_intentions_idx] = 0
    new_df_survey.iloc[:, cols_grades_idx] = "nan"
    if aggregation == AggregationMode.FOUR_MENTIONS:
        new_df_survey.loc[new_df_survey.index, "nombre_mentions"] = 4
    else:
        raise NotImplementedError(f"This method {aggregation} is not implemented ")

    # Add the numbers together
    for i, ng in enumerate(new_grades):
        new_df_survey.iloc[:, cols_grades_idx[i]] = ng
        potential_grades = df_corresponding_grades[df_corresponding_grades[col] == ng]["mention"]
        # find if al the potential grades are in this survey
        for pg in potential_grades:
            pg_in_grades_survey = pg == grades_survey
            if pg_in_grades_survey.any():
                idx = np.where(pg_in_grades_survey)[0][0]
                new_df_survey.iloc[:, cols_intentions_idx[i]] += df_survey.iloc[:, cols_intentions_idx[idx]]

    return new_df_survey


def load_surveys(
    csv_file: Path,
    no_opinion_mode: bool = True,
    candidates: Candidacy = None,
    aggregation: AggregationMode = None,
    polling_organization: PollingOrganizations = None,
):
    """
    normalize file

    Parameters
    ----------
    csv_file: Path
        Path of the  file which contains all the data of vote / survey
    no_opinion_mode: bool
        remove or not the undecided grades
    candidates: Candidacy
        how to manage candidacies
    aggregation: AggregationMode
        how to manage Aggregation of several grades
    polling_organization: PollingOrganizations
        select polling organization
    Returns
    -------
    Return the DataFrame df with all surveys inside
    """
    if candidates is None:
        candidates = Candidacy.ALL
    if aggregation is None:
        aggregation = AggregationMode.NO_AGGREGATION
    if polling_organization is None:
        polling_organization = PollingOrganizations.ALL

    df_surveys = pd.read_csv(csv_file, na_filter=False)
    df_standardisation = pd.read_csv("standardisation.csv", na_filter=False)

    if polling_organization != PollingOrganizations.ALL:
        df_surveys = df_surveys[df_surveys["nom_institut"] == polling_organization.value]

    # remove undecided
    if no_opinion_mode:
        df_surveys["sans_opinion"] = None

        df_undecided_grades = df_standardisation[df_standardisation["to_4_mentions"] == "sans opinion"]
        surveys = get_list_survey(df_surveys)

        for survey in surveys:
            print(survey)
            # select the survey
            df_survey = df_surveys[df_surveys["id"] == survey].copy()
            # remove undecided grades
            df_survey = remove_undecided(df_survey, df_undecided_grades)

            # refill the dataframe of surveys
            df_surveys[df_surveys["id"] == survey] = df_survey

    if candidates == Candidacy.ALL_CANDIDATES_FROM_BEGINNING:
        df_surveys = df_surveys[df_surveys["candidat_presidentielle"] == True]

    if candidates == Candidacy.ALL_CURRENT_CANDIDATES:
        df_surveys = df_surveys[df_surveys["candidat_presidentielle"] == True]
        df_surveys = df_surveys[df_surveys["retrait_candidature"] == "nan"]

    if candidates == Candidacy.ALL_CURRENT_CANDIDATES_WITH_ENOUGH_DATA:
        df_surveys = df_surveys[df_surveys["candidat_presidentielle"] == True]
        df_surveys = df_surveys[df_surveys["retrait_candidature"] == "nan"]
        df_surveys = df_surveys[df_surveys["candidat"] != "Nathalie Arthaud"]  # todo: dont hard code
        df_surveys = df_surveys[
            df_surveys["candidat"] != "Jean Lassalle"
        ]  # todo: remove candidates with only two dots instead.

    if aggregation != AggregationMode.NO_AGGREGATION:

        surveys = get_list_survey(df_surveys)

        for survey in surveys:
            print(survey)
            # select the survey
            df_survey = df_surveys[df_surveys["id"] == survey].copy()
            # remove undecided grades
            df_survey = convert_grades(df_survey, df_standardisation, aggregation, no_opinion_mode)
            # refill the dataframe of surveys
            df_surveys[df_surveys["id"] == survey] = df_survey

    return df_surveys
