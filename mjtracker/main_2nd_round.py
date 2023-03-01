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
from misc.enums import Candidacy, AggregationMode, PollingOrganizations, UntilRound

# todo: moyennes / ecart-type grades sur un profil de merite.
# todo: video d'evolution du graphique (baromètre animé)


class Arguments(tap.Tap):
    merit_profiles: bool = True
    comparison_ranking_plot: bool = True
    ranking_plot: bool = True
    time_merit_profile: bool = True
    ranked_time_merit_profile: bool = True
    comparison_intention: bool = True
    test: bool = False
    show: bool = True
    html: bool = False
    png: bool = False
    json: bool = False
    csv: Path = Path("../presidentielle_jm.csv")
    dest: Path = Path("../trackerapp/data/graphs/")


def main(args: Arguments):
    args.dest.mkdir(exist_ok=True, parents=True)
    aggregation = AggregationMode.NO_AGGREGATION
    polls = PollingOrganizations.MIEUX_VOTER
    # df = load_surveys(
    #     args.csv,
    #     no_opinion_mode=True,
    #     candidates=Candidacy.SECOND_ROUND,
    #     aggregation=aggregation,
    #     polling_organization=polls,
    #     rolling_data=False,
    # )
    #
    # # smp_data = SMPData()
    # # apply mj on the whole dataframe for each survey
    # df = apply_mj(df, rolling_mj=False)
    # # generate merit profile figures
    # batch_merit_profile(df, args)
    # # # generate ranking figures
    # batch_ranking(df, args)
    # # # generate comparison ranking figures
    # # batch_comparison_ranking(df, smp_data, args)
    # # # generate time merit profile figures
    # batch_time_merit_profile(df, args, aggregation, polls=polls)
    # # # generate ranked time merit profile figures
    # batch_ranked_time_merit_profile(df, args, aggregation, polls=polls)
    #
    # polls = PollingOrganizations.MIEUX_VOTER
    # df = load_surveys(
    #     Path("../presidentielle_2nd_tour_jm_abstensionistes.csv"),
    #     no_opinion_mode=True,
    #     candidates=Candidacy.SECOND_ROUND,
    #     aggregation=aggregation,
    #     polling_organization=polls,
    #     rolling_data=False,
    # )
    #
    # df = apply_mj(df, rolling_mj=False)
    # batch_ranked_time_merit_profile(df, args, aggregation, polls=polls)
    #
    # df = load_surveys(
    #     Path("../presidentielle_2nd_tour_jm_melenchonistes.csv"),
    #     no_opinion_mode=True,
    #     candidates=Candidacy.SECOND_ROUND,
    #     aggregation=aggregation,
    #     polling_organization=polls,
    #     rolling_data=False,
    # )
    #
    # df = apply_mj(df, rolling_mj=False)
    # batch_ranked_time_merit_profile(df, args, aggregation, polls=polls)

    # df = load_surveys(
    #     Path("../presidentielle_2nd_tour_jm_macron.csv"),
    #     no_opinion_mode=True,
    #     candidates=Candidacy.SECOND_ROUND,
    #     aggregation=aggregation,
    #     polling_organization=polls,
    #     rolling_data=False,
    # )
    #
    # df = apply_mj(df, rolling_mj=False)
    # batch_ranked_time_merit_profile(df, args, aggregation, polls=polls)

    df = load_surveys(
        Path("../presidentielle_2nd_tour_jm_lepen.csv"),
        no_opinion_mode=True,
        candidates=Candidacy.SECOND_ROUND,
        aggregation=aggregation,
        polling_organization=polls,
        rolling_data=False,
    )

    df = apply_mj(df, rolling_mj=False)
    batch_ranked_time_merit_profile(df, args, aggregation, polls=polls)

if __name__ == "__main__":
    args = Arguments().parse_args()
    print(args)

    main(args)
