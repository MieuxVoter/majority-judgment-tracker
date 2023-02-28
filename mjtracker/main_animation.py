from pathlib import Path
import tap
from utils import get_list_survey, get_grades
from plots import plot_merit_profiles, plot_animated_merit_profile
from interface_mj import apply_mj
from load_surveys import load_surveys
from misc.enums import Candidacy, AggregationMode, PollingOrganizations, UntilRound

class Arguments(tap.Tap):
    merit_profiles: bool = True
    comparison_ranking_plot: bool = True
    ranking_plot: bool = True
    time_merit_profile: bool = True
    ranked_time_merit_profile: bool = True
    comparison_intention: bool = True
    test: bool = False
    show: bool = True
    html: bool = True
    png: bool = True
    json: bool = True
    csv: Path = Path("../presidentielle_jm.csv")
    dest: Path = Path("../trackerapp/data/graphs/")


def main(args: Arguments):
    args.dest.mkdir(exist_ok=True, parents=True)
    aggregation = AggregationMode.NO_AGGREGATION
    df = load_surveys(
        args.csv,
        no_opinion_mode=True,
        candidates=Candidacy.ALL_CURRENT_CANDIDATES,
        aggregation=aggregation,
        polling_organization=PollingOrganizations.ALL,
        until_round=UntilRound.FIRST,
        rolling_data=False,
    )

    # apply mj on the whole dataframe for each survey
    df = apply_mj(df, rolling_mj=False)
    # generate merit profile figures

    surveys = get_list_survey(df)
    survey = surveys[0]

    df_survey = df[df["id"] == survey].copy()

    first_idx = df_survey.first_valid_index()
    source = df_survey["nom_institut"].loc[first_idx]
    sponsor = df_survey["commanditaire"].loc[first_idx]
    date = df_survey["fin_enquete"].loc[first_idx]
    nb_grades = df_survey["nombre_mentions"].unique()[0]
    grades = get_grades(df_survey, nb_grades)

    fig = plot_animated_merit_profile(
        df=df_survey,
        grades=grades,
        source=source,
        date=date,
        sponsor=sponsor,
        show_no_opinion=True,
    )
    filename = f"{survey}"
    print(filename)
    fig.show()
    # export as a gif for the animation
    # fig.write_image(f"{args.dest}/{filename}.gif")


if __name__ == "__main__":
    args = Arguments().parse_args()
    print(args)

    main(args)
