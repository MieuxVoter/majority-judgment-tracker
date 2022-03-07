import pandas as pd
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


def get_grades(df: DataFrame, nb_mentions: int = 7) -> list:
    list_col = df.columns.to_list()
    mentions_colheader = [s for s in list_col if "mention" in s and not "intention" in s and not "nombre" in s]
    mentions_colheader = mentions_colheader[:nb_mentions]
    numpy_mention = df[mentions_colheader].to_numpy().tolist()[0]

    numpy_mention = [m for m in numpy_mention if m != "nan"]
    return numpy_mention


def get_candidates(df: DataFrame):
    return df["candidat"].unique()


def load_uninominal_ranks():
    df_uninominal = pd.read_json(
        "https://raw.githubusercontent.com/rozierguillaume/electracker/main/data/output/intentionsCandidatsMoyenneMobile14Jours.json"
    )

    # Create a new dataframe
    df_rank_uninominal = pd.DataFrame(columns=["candidat", "fin_enquete", "valeur", "rang"])
    for row in df_uninominal.iterrows():
        dict_moy = row[1]["candidats"]["intentions_moy_14d"]
        for d, v in zip(dict_moy["fin_enquete"], dict_moy["valeur"]):
            row_to_add = dict(candidat=row[0], fin_enquete=d, valeur=v, rang=None)
            df_dictionary = pd.DataFrame([row_to_add])
            df_rank_uninominal = pd.concat([df_rank_uninominal, df_dictionary], ignore_index=True)

    # Compute the rank of every candidates
    df_rank_uninominal = df_rank_uninominal.sort_values(by=["fin_enquete", "valeur"], ascending=(True, False))
    dates = df_rank_uninominal["fin_enquete"].unique()
    for d in dates:
        nb_candidates = len(df_rank_uninominal[df_rank_uninominal["fin_enquete"] == d])
        # index_col = df_rank_uninominal.columns.get_loc("rang")
        index_row = df_rank_uninominal.index[df_rank_uninominal["fin_enquete"] == d]
        df_rank_uninominal.loc[index_row, "rang"] = [i + 1 for i in range(nb_candidates)]

    return df_rank_uninominal
