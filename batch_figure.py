from plots import (
    plot_merit_profiles,
    ranking_plot,
    comparison_ranking_plot,
    plot_time_merit_profile,
    plot_time_merit_profile_all_polls,
    plot_ranked_time_merit_profile,
    plot_comparison_intention,
    export_fig,
)
from utils import (
    get_list_survey,
    get_grades,
    get_candidates,
)
from misc.enums import PollingOrganizations, AggregationMode
from smp_data import SMPData


def batch_merit_profile(df, args):
    surveys = get_list_survey(df)

    for survey in surveys:
        df_survey = df[df["id"] == survey].copy()

        first_idx = df_survey.first_valid_index()
        source = df_survey["nom_institut"].loc[first_idx]
        sponsor = df_survey["commanditaire"].loc[first_idx]
        date = df_survey["fin_enquete"].loc[first_idx]
        nb_grades = df_survey["nombre_mentions"].unique()[0]
        grades = get_grades(df_survey, nb_grades)

        if args.merit_profiles:
            fig = plot_merit_profiles(
                df=df_survey,
                grades=grades,
                auto_text=False,
                source=source,
                date=date,
                sponsor=sponsor,
                show_no_opinion=True,
            )
            filename = f"{survey}"
            print(filename)
            export_fig(fig, args, filename)


def batch_ranking(df, args, on_rolling_data: bool = False):
    for poll in PollingOrganizations:
        df_poll = df[df["nom_institut"] == poll.value].copy() if poll != PollingOrganizations.ALL else df.copy()
        first_idx = df_poll.first_valid_index()
        source = poll.value
        label = source if poll != PollingOrganizations.ALL else poll.name
        sponsor = df_poll["commanditaire"].loc[first_idx] if poll != PollingOrganizations.ALL else None

        if args.ranking_plot:
            fig, annotations = ranking_plot(
                df_poll,
                source=source,
                sponsor=sponsor,
                show_grade_area=True,
                breaks_in_names=True,
                show_rank=False,
                on_rolling_data=on_rolling_data,
            )
            filename = f"ranking_plot_{label}"
            print(filename)
            export_fig(fig, args, filename)


def batch_comparison_ranking(df, smp_data: SMPData, args, on_rolling_data: bool = False):
    for poll in PollingOrganizations:
        df_poll = df[df["nom_institut"] == poll.value].copy() if poll != PollingOrganizations.ALL else df.copy()
        source = poll.value
        label = source if poll != PollingOrganizations.ALL else poll.name
        roll = "_roll" if on_rolling_data else ""
        if args.comparison_ranking_plot:
            fig = comparison_ranking_plot(
                df_poll, smp_data=smp_data, source=source, on_rolling_data=on_rolling_data
            )
            filename = f"comparison_ranking_plot_{label}{roll}"
            print(filename)
            export_fig(fig, args, filename)


def batch_time_merit_profile(df, args, aggregation, polls: PollingOrganizations = PollingOrganizations):
    for poll in polls:
        if poll == PollingOrganizations.ALL and aggregation == AggregationMode.NO_AGGREGATION:
            continue
        df_poll = df[df["nom_institut"] == poll.value].copy() if poll != PollingOrganizations.ALL else df.copy()
        first_idx = df_poll.first_valid_index()
        source = poll.value
        label = source if poll != PollingOrganizations.ALL else poll.name
        sponsor = df_poll["commanditaire"].loc[first_idx] if poll != PollingOrganizations.ALL else None
        aggregation_label = f"_{aggregation.name}" if aggregation != AggregationMode.NO_AGGREGATION else ""

        for c in get_candidates(df):
            temp_df = df_poll[df_poll["candidat"] == c]
            if temp_df.empty:
                continue
            if args.time_merit_profile:
                fig = plot_time_merit_profile(temp_df, source=source, sponsor=sponsor)
                filename = f"time_merit_profile{aggregation_label}_{c}_{label}"
                print(filename)
                export_fig(fig, args, filename)

    for c in get_candidates(df):
        temp_df = df[df["candidat"] == c]
        if args.time_merit_profile:
            fig = plot_time_merit_profile_all_polls(temp_df, aggregation)
            filename = f"time_merit_profile_comparison{aggregation_label}_{c}"
            print(filename)
            export_fig(fig, args, filename)


def batch_ranked_time_merit_profile(df, args, aggregation, polls: PollingOrganizations = PollingOrganizations):
    for poll in polls:
        if poll == PollingOrganizations.ALL and aggregation == AggregationMode.NO_AGGREGATION:
            continue
        df_poll = df[df["nom_institut"] == poll.value].copy() if poll != PollingOrganizations.ALL else df.copy()
        first_idx = df_poll.first_valid_index()
        source = poll.value
        label = source if poll != PollingOrganizations.ALL else poll.name
        sponsor = df_poll["commanditaire"].loc[first_idx] if poll != PollingOrganizations.ALL else None
        aggregation_label = f"_{aggregation.name}" if aggregation != AggregationMode.NO_AGGREGATION else ""

        if df_poll.empty:
            continue
        if args.ranked_time_merit_profile:
            fig = plot_ranked_time_merit_profile(df_poll, source=source, sponsor=sponsor, show_no_opinion=True)
            filename = f"ranked_time_merit_profile{aggregation_label}_{label}"
            print(filename)
            export_fig(fig, args, filename)


def batch_comparison_intention(
    df,
    smp_data: SMPData,
    args,
    aggregation,
    polls: PollingOrganizations = PollingOrganizations,
    on_rolling_data: bool = False,
):
    for poll in polls:
        if poll == PollingOrganizations.ALL and aggregation == AggregationMode.NO_AGGREGATION:
            continue
        df_poll = df[df["nom_institut"] == poll.value].copy() if poll != PollingOrganizations.ALL else df.copy()
        first_idx = df_poll.first_valid_index()
        source = poll.value
        label = source if poll != PollingOrganizations.ALL else poll.name
        sponsor = df_poll["commanditaire"].loc[first_idx] if poll != PollingOrganizations.ALL else None
        aggregation_label = f"_{aggregation.name}" if aggregation != AggregationMode.NO_AGGREGATION else ""

        if df_poll.empty:
            continue
        if args.comparison_intention:
            for c in get_candidates(df_poll):
                temp_df = df_poll[df_poll["candidat"] == c]
                fig = plot_comparison_intention(
                    temp_df,
                    smp_data=smp_data,
                    source=source,
                    sponsor=sponsor,
                    on_rolling_data=on_rolling_data,
                )
                filename = f"intention_{label}{aggregation_label}_{c}"
                print(filename)
                export_fig(fig, args, filename)


def batch_time_merit_profile_all(df, args, aggregation, on_rolling_data: bool = False):
    if aggregation == AggregationMode.NO_AGGREGATION:
        raise ValueError("Need to have an AggregationMode such as FOUR_MENTION to make it work.")

    poll = PollingOrganizations.ALL
    df_poll = df
    first_idx = df_poll.first_valid_index()
    source = poll.value
    label = poll.name
    sponsor = None
    aggregation_label = f"_{aggregation.name}"
    roll = "_roll" if on_rolling_data else ""

    for c in get_candidates(df):
        temp_df = df_poll[df_poll["candidat"] == c]
        if temp_df.empty:
            continue
        if args.time_merit_profile:
            fig = plot_time_merit_profile(temp_df, source=source, sponsor=sponsor, on_rolling_data=on_rolling_data)
            filename = f"time_merit_profile{aggregation_label}_{c}_{label}{roll}"
            print(filename)
            export_fig(fig, args, filename)
