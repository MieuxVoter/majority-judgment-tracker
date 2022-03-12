from plots import (
    plot_merit_profiles,
    ranking_plot,
    comparison_ranking_plot,
    plot_time_merit_profile,
    plot_time_merit_profile_all_polls,
    export_fig,
)
from utils import (
    get_list_survey,
    get_grades,
    get_candidates,
)
from misc.enums import PollingOrganizations, AggregationMode


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
            export_fig(fig, args, filename)


def batch_ranking(df, args):
    for poll in PollingOrganizations:
        df_poll = df[df["nom_institut"] == poll.value].copy() if poll != PollingOrganizations.ALL else df.copy()
        first_idx = df_poll.first_valid_index()
        source = poll.value
        label = source if poll != PollingOrganizations.ALL else poll.name
        sponsor = df_poll["commanditaire"].loc[first_idx] if poll != PollingOrganizations.ALL else None

        if args.ranking_plot:
            fig, annotations = ranking_plot(
                df_poll, source=source, sponsor=sponsor, show_grade_area=True, breaks_in_names=True, show_rank=False
            )
            filename = f"ranking_plot_{label}"
            export_fig(fig, args, filename)


def batch_comparison_ranking(df, args):
    for poll in PollingOrganizations:
        df_poll = df[df["nom_institut"] == poll.value].copy() if poll != PollingOrganizations.ALL else df.copy()
        source = poll.value
        label = source if poll != PollingOrganizations.ALL else poll.name

        if args.comparison_ranking_plot:
            fig = comparison_ranking_plot(df_poll, source=source)
            filename = f"comparison_ranking_plot_{label}"
            export_fig(fig, args, filename)


def batch_time_merit_profile(df, args, aggregation):
    for poll in PollingOrganizations:
        if poll == PollingOrganizations.ALL and aggregation == AggregationMode.NO_AGGREGATION:
            continue
        df_poll = df[df["nom_institut"] == poll.value].copy() if poll != PollingOrganizations.ALL else df.copy()
        first_idx = df_poll.first_valid_index()
        source = poll.value
        label = source if poll != PollingOrganizations.ALL else poll.name
        sponsor = df_poll["commanditaire"].loc[first_idx] if poll != PollingOrganizations.ALL else None
        aggregation_label = f"_{aggregation.name}" if aggregation != AggregationMode.NO_AGGREGATION else ""

        for c in get_candidates(df):
            print(c)
            temp_df = df_poll[df_poll["candidat"] == c]
            if temp_df.empty:
                continue
            if args.time_merit_profile:
                fig = plot_time_merit_profile(temp_df, source=source, sponsor=sponsor)
                filename = f"time_merit_profile{aggregation_label}_{c}_{label}"
                export_fig(fig, args, filename)

    for c in get_candidates(df):
        print(c)
        temp_df = df[df["candidat"] == c]
        if args.time_merit_profile:
            fig = plot_time_merit_profile_all_polls(temp_df, aggregation)
            filename = f"time_merit_profile_comparison{aggregation_label}_{c}"
            export_fig(fig, args, filename)
