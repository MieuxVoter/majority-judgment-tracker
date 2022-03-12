from pathlib import Path
import tap
from batch_figure import batch_merit_profile, batch_ranking, batch_time_merit_profile, batch_comparison_ranking
from plots import comparison_ranking_plot
from interface_mj import apply_mj
from load_surveys import load_surveys
from misc.enums import Candidacy, AggregationMode, PollingOrganizations


# todo: graphique classement en fonction des dates (avec mediane glissante)
# todo: moyennes / ecart-type grades sur un profil de merite.
# todo: video d'evolution du graphique (baromètre animé)


class Arguments(tap.Tap):
    merit_profiles: bool = False
    comparison_ranking_plot: bool = False
    ranking_plot: bool = False
    time_merit_profile: bool = False
    show: bool = False
    html: bool = False
    png: bool = False
    json: bool = False
    csv: Path = Path("presidentielle_jm.csv")
    dest: Path = Path("figs")


def main(args: Arguments):
    args.dest.mkdir(exist_ok=True)
    aggregation = AggregationMode.NO_AGGREGATION
    df = load_surveys(
        args.csv,
        no_opinion_mode=True,
        candidates=Candidacy.ALL_CURRENT_CANDIDATES_WITH_ENOUGH_DATA,
        aggregation=aggregation,
        polling_organization=PollingOrganizations.ALL,
    )

    # # apply mj on the whole dataframe for each survey
    df = apply_mj(df)
    # generate merit profile figures
    batch_merit_profile(df, args)
    # generate ranking figures
    batch_ranking(df, args)
    # generate comparison ranking figures
    batch_comparison_ranking(df, args)
    # generate time merit profile figures
    batch_time_merit_profile(df, args, aggregation)

    aggregation = AggregationMode.FOUR_MENTIONS
    df = load_surveys(
        args.csv,
        no_opinion_mode=True,
        candidates=Candidacy.ALL_CURRENT_CANDIDATES_WITH_ENOUGH_DATA,
        aggregation=aggregation,
        polling_organization=PollingOrganizations.ALL,
    )
    df = apply_mj(df)
    batch_time_merit_profile(df, args, aggregation)


if __name__ == "__main__":
    args = Arguments().parse_args()
    print(args)

    main(args)
