from pandas import DataFrame
import numpy as np


def get_list_survey(df: DataFrame):
    return df["id"].unique()


def get_intentions(df: DataFrame, nb_mentions: int = 7) -> object:
    list_col = df.columns.to_list()
    colheader = ["candidat"]
    colheader.extend(get_intentions_colheaders(df, nb_mentions))
    return df[colheader]


def get_intentions_colheaders(df: DataFrame, nb_mentions: int = 7):
    list_col = df.columns.to_list()
    intentions_colheader = [s for s in list_col if "intention" in s]
    return intentions_colheader[:nb_mentions]


def get_grades(df: DataFrame, nb_mentions: int = 7) -> object:
    list_col = df.columns.to_list()
    mentions_colheader = [s for s in list_col if "mention" in s and not "intention" in s and not "nombre" in s]
    mentions_colheader = mentions_colheader[:nb_mentions]
    numpy_mention = df[mentions_colheader].to_numpy().tolist()[0]
    return numpy_mention
