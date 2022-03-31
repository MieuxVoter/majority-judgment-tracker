import json
import pandas as pd
import datetime
import warnings

class Polldata:
    @staticmethod
    def getPanda(source):
        if not hasattr(Polldata, 'source'):
            print('initializing panda source ' + source)
            Polldata.source=source
            Polldata.panda=pd.read_csv("https://raw.githubusercontent.com/nsppolls/nsppolls/master/presidentielle.csv")
        print('using panda source ' + Polldata.source)
        return Polldata.panda

def load_data_from_nsppolls():
    df = Polldata.getPanda("https://raw.githubusercontent.com/nsppolls/nsppolls/master/presidentielle.csv")
    df = df[df["tour"] == "Premier tour"]
    df = df.sort_values(by="fin_enquete")
    df = df[df["fin_enquete"] > "2021-09-01"]

    CANDIDATS = {
        "Marine Le Pen": {"couleur": "#04006e"},
        "Emmanuel Macron": {"couleur": "#0095eb"},
        "Yannick Jadot": {"couleur": "#0bb029"},
        "Jean-Luc Mélenchon": {"couleur": "#de001e"},
        "Fabien Roussel": {"couleur": "#940014"},
        "Valérie Pécresse": {"couleur": "#0242e3"},
        "Anne Hidalgo": {"couleur": "#b339a4"},
        "Christiane Taubira": {"couleur": "#c7a71a"},
        "Eric Zemmour": {"couleur": "#010038"},
        "Nathalie Arthaud": {"couleur": "#8f0007"},
        "Jean Lassalle": {"couleur": "#c96800"},
        "Philippe Poutou": {"couleur": "#82001a"},
        "François Asselineau": {"couleur": "#12004f"},
        "Nicolas Dupont-Aignan": {"couleur": "#3a84c4"},
    }

    dict_candidats = {}
    derniere_intention = pd.DataFrame()  # columns=["candidat", "intentions"])
    for candidat in CANDIDATS:
        df_temp = df[df["candidat"] == candidat]
        df_temp.index = pd.to_datetime(df_temp["fin_enquete"])

        df_temp_rolling = (
            df_temp[["intentions", "erreur_inf", "erreur_sup"]].rolling("10d", min_periods=1).mean().shift(-5).dropna()
        )
        df_temp_rolling_std = df_temp[["intentions"]].rolling("10d", min_periods=1).std().shift(-5).dropna()

        df_temp_rolling = round(df_temp_rolling.resample("1d").mean().dropna(), 2).rolling(window=7).mean().dropna()
        df_temp_rolling_std = (
            round(df_temp_rolling_std.resample("1d").mean().dropna(), 2).rolling(window=7).mean().dropna()
        )
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            derniere_intention = derniere_intention.append(
                {"candidat": candidat, "intentions": df_temp_rolling.intentions.to_list()[-1]}, ignore_index=True
            )

        dict_candidats[candidat] = {
            "intentions_moy_14d": {
                "fin_enquete": df_temp_rolling.index.strftime("%Y-%m-%d").to_list(),
                "valeur": df_temp_rolling.intentions.to_list(),
                "std": df_temp_rolling_std.intentions.to_list(),
                "erreur_inf": df_temp_rolling.erreur_inf.to_list(),
                "erreur_sup": df_temp_rolling.erreur_sup.to_list(),
            },
            "intentions": {
                "fin_enquete": df_temp.index.strftime("%Y-%m-%d").to_list(),
                "valeur": df_temp.intentions.to_list(),
            },
            "derniers_sondages": [],
            "couleur": CANDIDATS[candidat]["couleur"],
        }

    dict_donnees = {
        "dernier_sondage": df["fin_enquete"].max(),
        "mise_a_jour": datetime.datetime.now().strftime(format="%Y-%m-%d %H:%M"),
        "candidats": dict_candidats,
    }

    with open("intentionsCandidatsMoyenneMobile14Jours.json", "w") as outfile:
        json.dump(dict_donnees, outfile)

    return pd.read_json("intentionsCandidatsMoyenneMobile14Jours.json")


def load_uninominal_ranks():
    df_uninominal = load_data_from_nsppolls()

    # Create a new dataframe
    df_rank_uninominal = pd.DataFrame(columns=["candidat", "fin_enquete", "valeur", "rang", "erreur_sup", "erreur_inf"])
    for row in df_uninominal.iterrows():
        dict_moy = row[1]["candidats"]["intentions_moy_14d"]
        for d, v, sup, inf in zip(
            dict_moy["fin_enquete"],
            dict_moy["valeur"],
            dict_moy["erreur_inf"],
            dict_moy["erreur_sup"],
        ):
            row_to_add = dict(
                candidat=row[0], fin_enquete=d, valeur=v, rang=None, erreur_sup=sup, erreur_inf=inf  # intentions=i,
            )
            df_dictionary = pd.DataFrame([row_to_add])
            df_rank_uninominal = pd.concat([df_rank_uninominal, df_dictionary], ignore_index=True)

    # Fill date without value for some candidates
    for c in df_rank_uninominal["candidat"].unique():
        temp_df = df_rank_uninominal[df_rank_uninominal["candidat"] == c]
        date_min = temp_df["fin_enquete"].min()
        date_max = temp_df["fin_enquete"].max()
        for d in df_rank_uninominal["fin_enquete"].unique():
            if (d > date_min) and (d < date_max) and temp_df[temp_df["fin_enquete"] == d].empty:
                idx = temp_df["fin_enquete"].searchsorted(d)
                v = temp_df["valeur"].iloc[idx - 1]
                sup = temp_df["erreur_sup"].iloc[idx - 1]
                inf = temp_df["erreur_inf"].iloc[idx - 1]
                row_to_add = dict(candidat=c, fin_enquete=d, valeur=v, rang=None, erreur_sup=sup, erreur_inf=inf)
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


def load_uninominal_data():
    df_uninominal = load_data_from_nsppolls()

    # Create a new dataframe
    df_uninominal_data = pd.DataFrame(columns=["candidat", "fin_enquete", "intentions"])
    for row in df_uninominal.iterrows():
        for (
            d,
            i,
        ) in zip(row[1]["candidats"]["intentions"]["fin_enquete"], row[1]["candidats"]["intentions"]["valeur"]):
            row_to_add = dict(
                candidat=row[0],
                fin_enquete=d,
                intentions=i,
            )
            df_dictionary = pd.DataFrame([row_to_add])
            df_uninominal_data = pd.concat([df_uninominal_data, df_dictionary], ignore_index=True)

    return df_uninominal_data
