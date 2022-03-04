from pathlib import Path
import pandas as pd
import numpy as np
import tap
from plots import plot_merit_profiles, ranking_plot
from utils import (
    get_list_survey,
    get_grades,
)
from interface_mj import sort_candidates_mj
from load_surveys import load_surveys
from misc.enums import Candidacy, AggregationMode, PollingOrganizations

# todo: graphique classement en fonction des dates (avec mediane glissante)
# todo: moyennes / ecart-type grades sur un profil de merite.
# todo: video d'evolution du graphique (baromètre animé)


class Arguments(tap.Tap):
    merit_profiles: bool = False
    ranking_plot: bool = False
    show: bool = False
    html: bool = False
    png: bool = False
    json: bool = False
    csv: Path = Path("presidentielle_jm.csv")
    dest: Path = Path("figs")



def main(args: Arguments):
    args.dest.mkdir(exist_ok=True)

    df = load_surveys(
        args.csv,
        no_opinion_mode=True,
        candidates=Candidacy.ALL_CURRENT_CANDIDATES_WITH_ENOUGH_DATA,
        aggregation=AggregationMode.FOUR_MENTIONS,
        polling_organization=PollingOrganizations.ALL,
    )

    # Compute the rank for each survey
    df["rang"] = None

    surveys = get_list_survey(df)

    for survey in surveys:
        print(survey)
        # only the chosen survey
        df_survey = df[df["id"] == survey].copy()

        nb_grades = df_survey["nombre_mentions"].unique()[0]
        grades = get_grades(df_survey, nb_grades)
        first_idx = df_survey.first_valid_index()
        source = df_survey["nom_institut"].loc[first_idx]
        sponsor = df_survey["commanditaire"].loc[first_idx]
        date = df_survey["fin_enquete"].loc[first_idx]

        df_with_rank = sort_candidates_mj(df_survey, nb_grades)

        # refill the dataframe of surveys
        df[df["id"] == survey] = df_with_rank

        if args.merit_profiles:
            fig = plot_merit_profiles(
                df=df_with_rank,
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
            if args.json:
                fig.write_json(f"{args.dest}/{survey}.json")
            if args.png:
                fig.write_image(f"{args.dest}/{survey}.png")
            if args.json:
                fig.write_json(f"{args.dest}/{survey}.json")

    if args.ranking_plot:
        fig = ranking_plot(df)
        if args.show:
            fig.show()
        if args.html:
            fig.write_html(f"{args.dest}/ranking_plot.html")
        if args.png:
            fig.write_image(f"{args.dest}/ranking_plot.png")
        if args.json:
            fig.write_json(f"{args.dest}/ranking_plot.json")


if __name__ == "__main__":
    args = Arguments().parse_args()
    print(args)

    main(args)
