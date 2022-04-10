from pathlib import Path
import tap
from batch_figure import (
    batch_merit_profile,
    batch_ranking,
    batch_time_merit_profile,
    batch_comparison_ranking,
    batch_time_merit_profile_all,
    batch_ranked_time_merit_profile,
    batch_comparison_intention,
)
from interface_mj import apply_mj
from load_surveys import load_surveys
from smp_data import SMPData
from misc.enums import Candidacy, AggregationMode, PollingOrganizations

# todo: moyennes / ecart-type grades sur un profil de merite.
# todo: video d'evolution du graphique (baromètre animé)


class Arguments(tap.Tap):
    merit_profiles: bool = False
    comparison_ranking_plot: bool = False
    ranking_plot: bool = False
    time_merit_profile: bool = False
    ranked_time_merit_profile: bool = False
    comparison_intention: bool = True
    test: bool = False
    show: bool = False
    html: bool = False
    png: bool = True
    json: bool = False
    csv: Path = Path("presidentielle_jm.csv")
    dest: Path = Path("trackerapp/data/graphs/")


def main(args: Arguments):
    args.dest.mkdir(exist_ok=True, parents=True)
    aggregation = AggregationMode.NO_AGGREGATION
    df = load_surveys(
        args.csv,
        no_opinion_mode=True,
        candidates=Candidacy.ALL_CURRENT_CANDIDATES,
        aggregation=aggregation,
        polling_organization=PollingOrganizations.ALL,
        rolling_data=False,
    )

    smp_data = SMPData()
    # apply mj on the whole dataframe for each survey
    df = apply_mj(df, rolling_mj=False)
    # generate merit profile figures
    batch_merit_profile(df, args)
    if not args.test:
        # # generate ranking figures
        batch_ranking(df, args)
        # # generate comparison ranking figures
        batch_comparison_ranking(df, smp_data, args)
        # # generate time merit profile figures
        batch_time_merit_profile(df, args, aggregation)
        # # generate ranked time merit profile figures
        batch_ranked_time_merit_profile(df, args, aggregation)
        # comparison uninominal per candidates
        batch_comparison_intention(df, smp_data, args, aggregation)

        aggregation = AggregationMode.FOUR_MENTIONS
        df = load_surveys(
            args.csv,
            no_opinion_mode=True,
            candidates=Candidacy.ALL_CURRENT_CANDIDATES_WITH_ENOUGH_DATA,
            aggregation=aggregation,
            polling_organization=PollingOrganizations.ALL,
            rolling_data=True,
        )
        df = apply_mj(df, rolling_mj=False)
        df = apply_mj(df, rolling_mj=True)
        batch_time_merit_profile_all(df, args, aggregation, on_rolling_data=False)
        batch_time_merit_profile_all(df, args, aggregation, on_rolling_data=True)
        batch_comparison_ranking(df, smp_data, args, on_rolling_data=True)


if __name__ == "__main__":
    args = Arguments().parse_args()
    print(args)

    main(args)
