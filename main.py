from pathlib import Path
import pandas as pd
import numpy as np
import tap
from plots import plot_merit_profiles
from utils import (
    get_list_survey,
    get_grades,
)
from interface_mj import sort_candidates_mj

# todo: handle sans opinion if case
# todo: graphique classement en fonction des dates (avec mediane glissante)
# todo: moyennes / ecart-type grades sur un profil de merite.
# todo: video d'evolution du graphique (baromètre animé)


class Arguments(tap.Tap):
    show: bool = False
    html: bool = False
    png: bool = False
    csv: Path = Path("presidentielle_jm.csv")
    dest: Path = Path("figs")


def main(args: Arguments):
    args.dest.mkdir(exist_ok=True)

    df = pd.read_csv(args.csv)
    surveys = get_list_survey(df)

    for survey in surveys:
        # only the chosen survey
        df_survey = df[df["id"] == survey]

        nb_grades = df_survey["nombre_mentions"].unique()[0]
        grades = get_grades(df_survey, nb_grades)
        first_idx = df_survey.first_valid_index()
        source = df_survey["nom_institut"].loc[first_idx]
        sponsor = df_survey["commanditaire"].loc[first_idx]
        date = df_survey["fin_enquete"].loc[first_idx]

        df_sorted = sort_candidates_mj(df_survey, nb_grades)

        fig = plot_merit_profiles(
            df=df_sorted,
            grades=grades,
            auto_text=False,
            source=source,
            date=date,
            sponsor=sponsor,
        )

        if args.show:
            fig.show()
        if args.html:
            fig.write_html(f"{args.dest}/{survey}.html")
        if args.png:
            fig.write_image(f"{args.dest}/{survey}.png")


if __name__ == "__main__":
    args = Arguments().parse_args()
    print(args)

    main(args)
