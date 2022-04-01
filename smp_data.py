import json
import pandas as pd
import datetime
import warnings


class SMPData:
    """
    Single-Member Plurality Voting Data from nsppolls.fr and to transform it into a pandas dataframe.

    Attributes
    ----------
    source : str
        The source of the data (nsppolls.fr).
    df_raw : pd.DataFrame
        The raw data from the csv file.
    df_treated : pd.DataFrame
        The dataframe with the data treated (moving average, etc.).

    Methods
    -------
    _treatment()
        Treat the raw dataframe into a nice dataframe.
    get_ranks()
        Load the uninomial ranks into a nice dataframe.
    get_intentions()
        Load the uninomial intentions into a nice dataframe.
    """

    def __init__(self, source_file: str = None):
        self.source = (
            "https://raw.githubusercontent.com/nsppolls/nsppolls/master/presidentielle.csv"
            if source_file is None
            else source_file
        )
        print("using panda source " + self.source)
        self.df_raw = pd.read_csv(self.source)
        self.df_treated = None
        self._treatement()

    def _treatement(self):
        """
        Treat the raw dataframe into a nice dataframe.

        """
        df = self.df_raw
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
                df_temp[["intentions", "erreur_inf", "erreur_sup"]]
                .rolling("10d", min_periods=1)
                .mean()
                .shift(-5)
                .dropna()
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

        self.df_treated = pd.read_json("intentionsCandidatsMoyenneMobile14Jours.json")

    def get_ranks(self):
        """
        Load the ranks of the candidates.

        Returns
        -------
        df_ranks_smp : pd.DataFrame
            Dataframe with the ranks of the candidates.
        """
        df_smp = self.df_treated

        # Create a new dataframe
        df_rank_smp = pd.DataFrame(
            columns=["candidat", "fin_enquete", "valeur", "rang", "erreur_sup", "erreur_inf"]
        )
        for row in df_smp.iterrows():
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
                df_rank_smp = pd.concat([df_rank_smp, df_dictionary], ignore_index=True)

        # Fill date without value for some candidates
        for c in df_rank_smp["candidat"].unique():
            temp_df = df_rank_smp[df_rank_smp["candidat"] == c]
            date_min = temp_df["fin_enquete"].min()
            date_max = temp_df["fin_enquete"].max()
            for d in df_rank_smp["fin_enquete"].unique():
                if (d > date_min) and (d < date_max) and temp_df[temp_df["fin_enquete"] == d].empty:
                    idx = temp_df["fin_enquete"].searchsorted(d)
                    v = temp_df["valeur"].iloc[idx - 1]
                    sup = temp_df["erreur_sup"].iloc[idx - 1]
                    inf = temp_df["erreur_inf"].iloc[idx - 1]
                    row_to_add = dict(candidat=c, fin_enquete=d, valeur=v, rang=None, erreur_sup=sup, erreur_inf=inf)
                    df_dictionary = pd.DataFrame([row_to_add])
                    df_rank_smp = pd.concat([df_rank_smp, df_dictionary], ignore_index=True)

        # Compute the rank of every candidates
        df_rank_smp = df_rank_smp.sort_values(by=["fin_enquete", "valeur"], ascending=(True, False))
        dates = df_rank_smp["fin_enquete"].unique()
        for d in dates:
            nb_candidates = len(df_rank_smp[df_rank_smp["fin_enquete"] == d])
            index_row = df_rank_smp.index[df_rank_smp["fin_enquete"] == d]
            df_rank_smp.loc[index_row, "rang"] = [i + 1 for i in range(nb_candidates)]

        return df_rank_smp

    def get_intentions(self):
        """
        Load the intentions of votes for each candidate.

        Returns
        -------
        df_smp : pd.DataFrame
            Dataframe with the intentions of votes for each candidate.
        """
        df_smp = self.df_treated

        # Create a new dataframe
        df_smp_data = pd.DataFrame(columns=["candidat", "fin_enquete", "intentions"])
        for row in df_smp.iterrows():
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
                df_smp_data = pd.concat([df_smp_data, df_dictionary], ignore_index=True)

        return df_smp_data
