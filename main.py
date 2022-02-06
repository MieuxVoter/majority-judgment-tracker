import pandas as pd
from pandas import DataFrame
import numpy as np
from plots import plot_merit_profiles
from utils import (
    get_list_survey,
    get_intentions,
    get_intentions_colheaders,
    get_grades,
)
from interface_mj import sort_candidates_mj

# todo: handle sans opinion if case
# todo: graphique classement en fonction des dates (avec mediane glissante)
# todo: moyennes / ecart-type grades sur un profil de merite.
# todo: video d'evolution du graphique (baromètre animé)

# import matplotlib.pyplot as plt


def main():
    df = pd.read_csv("presidentielle_jm.csv")

    surveys = get_list_survey(df)
    for survey in surveys:

        # only the chosen survey
        df_survey = df[df["id"] == survey]

        nb_grades = df_survey["nombre_mentions"].unique()[0]
        grades = get_grades(df_survey, nb_grades)
        first_idx = df_survey.first_valid_index()
        source = df_survey['nom_institut'].loc[first_idx]
        sponsor = df_survey["commanditaire"].loc[first_idx]
        date = df_survey["fin_enquete"].loc[first_idx]

        df_sorted = sort_candidates_mj(df_survey, nb_grades)

        plot_merit_profiles(
            df=df_sorted,
            grades=grades,
            auto_text=False,
            filename=survey,
            export_html=True,
            show=True,
            source=source,
            date=date,
            sponsor=sponsor,
        )


if __name__ == "__main__":
    main()
