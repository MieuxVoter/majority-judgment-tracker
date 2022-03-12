from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from seaborn import color_palette
from pandas import DataFrame
from utils import get_intentions_colheaders, get_candidates, get_grades, load_uninominal_ranks, rank2str
from misc.enums import PollingOrganizations, AggregationMode


def plot_merit_profiles(
    df: DataFrame,
    grades: list,
    auto_text: bool = True,
    font_size: int = 20,
    date: str = None,
    sponsor: str = None,
    source: str = None,
    show_no_opinion: bool = True,
):
    df = df.copy()

    nb_grades = len(grades)

    # compute the list sorted of candidat names to order y axis.
    candidat_list = list(df["candidat"])
    rank_list = list(df["rang"] - 1)
    sorted_candidat_list = [i[1] for i in sorted(zip(rank_list, candidat_list))]
    r_sorted_candidat_list = sorted_candidat_list.copy()
    r_sorted_candidat_list.reverse()

    colors = color_palette(palette="coolwarm", n_colors=nb_grades)
    color_dict = {f"intention_mention_{i + 1}": f"rgb{str(colors[i])}" for i in range(nb_grades)}
    fig = px.bar(
        df,
        x=get_intentions_colheaders(df, nb_grades),
        y="candidat",
        orientation="h",
        text_auto=auto_text,
        color_discrete_map=color_dict,
    )

    fig.update_traces(textfont_size=font_size, textangle=0, textposition="auto", cliponaxis=False, width=0.5)

    # replace variable names with grades
    new_names = {f"intention_mention_{i + 1}": grades[i] for i in range(nb_grades)}
    fig.for_each_trace(
        lambda t: t.update(
            name=new_names[t.name],
            legendgroup=new_names[t.name],
            hovertemplate=t.hovertemplate.replace(t.name, new_names[t.name]),
        )
    )

    # vertical line
    fig.add_vline(x=50, line_width=4, line_color="black")

    # Legend
    fig.update_layout(
        legend_title_text=None,
        autosize=True,
        legend=dict(orientation="h", xanchor="center", x=0.5, y=-0.05),  # 50 % of the figure width
    )

    fig.update(data=[{"hovertemplate": "Intention: %{x}<br>Candidat: %{y}"}])
    # todo: need to plot grades in hovertemplate.

    # no back ground
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    # xticks and y ticks
    # Add sans opinion to y tick label # todo : it may be simplified !
    if show_no_opinion and df["sans_opinion"].unique()[0] is not None:
        df["candidat_sans_opinion"] = None
        for ii, cell in enumerate(df["candidat"]):
            df["candidat_sans_opinion"].iat[ii] = (
                "<b>" + cell + "</b>" + "     <br><i>(sans opinion " + str(df["sans_opinion"].iloc[ii]) + "%)</i>     "
            )
        # compute the list sorted of candidat names to order y axis.
        candidat_list = list(df["candidat_sans_opinion"])
        rank_list = list(df["rang"] - 1)
        sorted_candidat_list = [i[1] for i in sorted(zip(rank_list, candidat_list))]
        r_sorted_candidat_no_opinion_list = sorted_candidat_list.copy()
        r_sorted_candidat_no_opinion_list.reverse()
        yticktext = r_sorted_candidat_no_opinion_list
    else:
        yticktext = ["<b>" + s + "</b>" + "     " for s in r_sorted_candidat_list]

    # xticks and y ticks
    fig.update_layout(
        xaxis=dict(
            range=[0, 100],
            tickmode="array",
            tickvals=[0, 20, 40, 60, 80, 100],
            ticktext=["0%", "20%", "40%", "60%", "80%", "100%"],
            tickfont_size=font_size,
            title="",  # intentions
        ),
        yaxis=dict(
            tickfont_size=font_size * 0.75,
            title="",  # candidat
            automargin=True,
            ticklabelposition="outside left",
            ticksuffix="   ",
            tickmode="array",
            tickvals=[i for i in range(len(df))],
            ticktext=yticktext,
            categoryorder="array",
            categoryarray=r_sorted_candidat_list,
        ),  # space
    )

    # Title and detailed
    date_str = ""
    source_str = ""
    sponsor_str = ""
    if date is not None:
        date_str = f"date: {date}, "
    if source is not None:
        source_str = f"source: {source}, "
    if sponsor is not None:
        sponsor_str = f"commanditaire: {sponsor}"
    title = "<b>Evaluation au jugement majoritaire</b> <br>" + f"<i>{date_str}{source_str}{sponsor_str}</i>"
    fig.update_layout(title=title, title_x=0.5)

    # font family
    fig.update_layout(font_family="arial")

    fig = add_image_to_fig(fig, x=0.8, y=0.95, sizex=0.2, sizey=0.2)

    # size of the figure
    fig.update_layout(width=1000, height=600)

    return fig


def ranking_plot(
    df,
    source: str = None,
    sponsor: str = None,
    show_best_grade: bool = True,
    show_rank: bool = True,
    show_no_opinion: bool = True,
    show_grade_area: bool = True,
    breaks_in_names: bool = True,
    fig: go.Figure = None,
    annotations: dict =None,
    row=None,
    col=None,
):
    # df = df[df["fin_enquete"] > "2021-12-01"]

    COLORS = {
        "Marine Le Pen": {"couleur": "#04006e"},
        "Emmanuel Macron": {"couleur": "#0095eb"},
        "Yannick Jadot": {"couleur": "#0bb029"},
        "Jean-Luc Mélenchon": {"couleur": "#de001e"},
        "Arnaud Montebourg": {"couleur": "#940014"},
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

    if fig is None:
        fig = go.Figure()

    df = df.sort_values(by="fin_enquete")

    # Grade area
    if show_grade_area:
        grades = get_grades(df)
        nb_grades = len(grades)
        c_rgb = color_palette(palette="coolwarm", n_colors=nb_grades)
        for g, c in zip(grades, c_rgb):
            temp_df = df[df["mention_majoritaire"] == g]
            if not temp_df.empty:
                c_alpha = str(f"rgba({c[0]},{c[1]},{c[2]},0.2)")
                # y_upper = get_all(df_results, d, "computation_time", "ci_up")
                x_date = temp_df["fin_enquete"].unique().tolist()
                y_upper = []
                y_lower = []
                for d in x_date:
                    y_upper.append(temp_df[temp_df["fin_enquete"] == d]["rang"].min() - 0.5)
                    y_lower.append(temp_df[temp_df["fin_enquete"] == d]["rang"].max() + 0.5)

                fig.add_scatter(
                    x=x_date + x_date[::-1],  # x, then x reversed
                    y=y_upper + y_lower[::-1],  # upper, then lower reversed
                    fill="toself",
                    fillcolor=c_alpha,
                    line=dict(color="rgba(255,255,255,0)"),
                    hoverinfo="skip",
                    showlegend=True,
                    name=g,
                    row=row,
                    col=col,
                    # legendgroup="grades",
                )

    annotations = [] if annotations is None else annotations
    for ii in get_candidates(df):
        temp_df = df[df["candidat"] == ii]
        fig.add_trace(
            go.Scatter(
                x=temp_df["fin_enquete"],
                y=temp_df["rang"],
                mode="lines",
                name=ii,
                marker=dict(color=COLORS[ii]["couleur"]),
                legendgroup=ii,
                showlegend=False,
            ),
            row=row,
            col=col,
        )

        fig.add_trace(
            go.Scatter(
                x=temp_df["fin_enquete"].iloc[0:1],
                y=temp_df["rang"].iloc[0:1],
                mode="markers",
                name=ii,
                marker=dict(color=COLORS[ii]["couleur"]),
                showlegend=False,
                legendgroup=ii,
            ),
            row=row,
            col=col,
        )

        fig.add_trace(
            go.Scatter(
                x=temp_df["fin_enquete"].iloc[-1:],
                y=temp_df["rang"].iloc[-1:],
                mode="markers",
                name=ii,
                marker=dict(color=COLORS[ii]["couleur"]),
                legendgroup=ii,
                showlegend=False,
            ),
            row=row,
            col=col,
        )

        # PREPARE ANNOTATIONS
        # name with break btw name and surname
        xref = f"x{col}" if row is not None else None
        yref = f"y{row}" if row is not None else None
        if breaks_in_names:
            idx_space = ii.find(" ")
            name_label = ii[:idx_space] + "<br>" + ii[idx_space + 1 :]
        else:
            name_label = ii
        size_annotations = 12

        # first dot annotation
        if temp_df["fin_enquete"].iloc[-1] != temp_df["fin_enquete"].iloc[0]:
            annotations.append(
                dict(
                    x=temp_df["fin_enquete"].iloc[0],
                    y=temp_df["rang"].iloc[0],
                    xanchor="right",
                    xshift=-10,
                    yanchor="middle",
                    text=f"<b>{name_label}</b>",
                    font=dict(family="Arial", size=size_annotations, color=COLORS[ii]["couleur"]),
                    showarrow=False,
                    xref=xref,
                    yref=yref,
                )
            )

        # Nice name label
        extended_name_label = f"<b>{name_label}</b>"
        if show_best_grade and not show_grade_area:
            extended_name_label += (
                "<br>"
                + temp_df["mention_majoritaire"].iloc[-1][0].upper()
                + temp_df["mention_majoritaire"].iloc[-1][1:]
            )
            if show_no_opinion and temp_df["sans_opinion"].iloc[-1] is not None:
                extended_name_label += " <i>(sans opinion " + str(temp_df["sans_opinion"].iloc[-1]) + "%)</i>"
        if show_rank:
            extended_name_label += " " + rank2str(temp_df["rang"].iloc[-1])
            if show_no_opinion and temp_df["sans_opinion"].iloc[-1] is not None:
                extended_name_label += " <i>(sans opinion " + str(temp_df["sans_opinion"].iloc[-1]) + "%)</i>"
        else:
            if show_no_opinion and temp_df["sans_opinion"].iloc[-1] is not None:
                extended_name_label += "<br><i>(sans opinion " + str(temp_df["sans_opinion"].iloc[-1]) + "%)</i>"

        # last dot annotation
        annotations.append(
            dict(
                x=temp_df["fin_enquete"].iloc[-1],
                y=temp_df["rang"].iloc[-1],
                xanchor="left",
                xshift=10,
                yanchor="middle",
                text=extended_name_label,
                font=dict(family="Arial", size=size_annotations, color=COLORS[ii]["couleur"]),
                showarrow=False,
                xref=xref,
                yref=yref,
            ),
        )

    fig.add_vline(x="2022-04-10", line_dash="dot")
    annotations.append(
        dict(
            x="2022-04-10",
            y=0.25,
            xanchor="left",
            xshift=10,
            yanchor="middle",
            text="1er Tour",
            font=dict(family="Arial", size=size_annotations),
            showarrow=False,
            xref=xref,
            yref=yref,
        )
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed", tick0=1, dtick=1, visible=False),
        annotations=annotations,
        plot_bgcolor="white",
        showlegend=True,
    )

    source_str = ""
    sponsor_str = ""
    if source is not None:
        source_str = f"source: {source}, "
    if sponsor is not None:
        sponsor_str = f"commanditaire: {sponsor}"

    date = df["fin_enquete"].max()
    title = (
        "<b>Classement des candidats à l'élection présidentielle 2022<br> au jugement majoritaire </b> <br>"
        + f"<i>{source_str}{sponsor_str}, dernier sondage: {date}.</i>"
    )
    fig.update_layout(title=title, title_x=0.5)
    fig = add_image_to_fig(fig, x=0.05, y=1.01, sizex=0.15, sizey=0.15)
    # SIZE OF THE FIGURE
    fig.update_layout(width=1200, height=800)
    # fig.show()
    # Legend
    fig.update_layout(
        legend_title_text="Mentions majoritaires",
        autosize=True,
        legend=dict(orientation="h", xanchor="center", x=0.5, y=-0.05),  # 50 % of the figure width/
    )
    return fig, annotations


def comparison_ranking_plot(
    df,
    source: str = None,
    sponsor: str = None,
    show_best_grade: bool = True,
    show_no_opinion: bool = True,
):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    vertical_spacing=0, column_titles=("Jugement majoritaire", "Scrutin uninominal"))

    fig, annotations = ranking_plot(
        df,
        source=source,
        sponsor=sponsor,
        show_best_grade=False,
        show_rank=True,
        show_no_opinion=False,
        show_grade_area=False,
        breaks_in_names=False,
        fig=fig,
        row=1,
        col=1,
    )

    df_uninominal = load_uninominal_ranks()
    df_uninominal = df_uninominal[df_uninominal["fin_enquete"] <= df["fin_enquete"].max()]
    df_uninominal = df_uninominal[df_uninominal["fin_enquete"] >= df["fin_enquete"].min()]
    # df_uninominal["rang"] = df_uninominal["rang"].__neg__()
    fig, annotations = ranking_plot(
        df_uninominal,
        source=None,
        sponsor=None,
        show_best_grade=False,
        show_rank=True,
        show_no_opinion=False,
        show_grade_area=False,
        breaks_in_names=False,
        fig=fig,
        annotations=annotations,
        row=2,
        col=1,
    )

    fig.update_yaxes(row=2, col=1, visible=False, autorange="reversed")
    fig.update_layout(width=1200, height=800)
    source_str = ""
    sponsor_str = ""
    if source is not None:
        source_str = f"source: {source}, "
    if sponsor is not None:
        sponsor_str = f"commanditaire: {sponsor}"

    date = df["fin_enquete"].max()
    title = (
            "<b>Comparaison des classement des candidats à l'élection présidentielle 2022<br> au jugement majoritaire et au scrutin uninominal</b><br>"
            + "<i>sources : mieux voter & nsppolls</i>"
    )
    fig.update_layout(title=title, title_x=0.5)

    return fig


def plot_time_merit_profile(df, sponsor, source):
    nb_grades = len(get_grades(df))
    colors = color_palette(palette="coolwarm", n_colors=nb_grades)
    color_dict = {f"intention_mention_{i + 1}": f"rgb{str(colors[i])}" for i in range(nb_grades)}

    col_intention = get_intentions_colheaders(df, nb_grades)
    y_cumsum = df[col_intention].to_numpy()

    fig = go.Figure()
    for g, col, cur_y in zip(get_grades(df), col_intention, y_cumsum.T):
        fig.add_trace(
            go.Scatter(
                x=df["fin_enquete"],
                y=cur_y,
                hoverinfo="x+y",
                mode="lines",
                line=dict(width=0.5, color=color_dict[col]),
                stackgroup="one",  # define stack group
                name=g,
            ),
        )

    for d in df["fin_enquete"]:
        fig.add_vline(x=d, line_dash="dot", line_width=1, line_color="black", opacity=0.2)

    fig.add_hline(
        y=50,
        line_dash="dot",
        line_width=4,
        line_color="black",
        annotation_text="50 %",
        annotation_position="bottom right",
    )
    fig.update_layout(
        yaxis_range=(0, 100),
        width=1200,
        height=800,
        legend_title_text="Mentions",
        autosize=True,
        legend=dict(orientation="h", xanchor="center", x=0.5, y=-0.05),  # 50 % of the figure width/
        yaxis=dict(
            tickfont_size=15,
            title="Mentions (%)",  # candidat
            automargin=True,
        ),
    )

    # Title and detailed
    date_str = ""
    source_str = ""
    sponsor_str = ""
    date = df["fin_enquete"].max()
    if source is not None:
        source_str = f"source: {source}, "
    if sponsor is not None:
        sponsor_str = f"commanditaire: {sponsor}"
    title = (
        f"<b>Evolution des mentions au jugement majoritaire"
        + f"<br> pour le candidat {df.candidat.unique().tolist()[0]}</b><br>"
        + f"<i>{source_str}{sponsor_str}, dernier sondage: {date}.</i>"
    )
    fig.update_layout(title=title, title_x=0.5)

    return fig


def plot_time_merit_profile_all_polls(df, aggregation):
    name_subplot = tuple([poll.value for poll in PollingOrganizations if poll != PollingOrganizations.ALL])
    fig = make_subplots(rows=3, cols=1, subplot_titles=name_subplot)
    count = 0
    date_max = df["fin_enquete"].max()
    date_min = df["fin_enquete"].min()

    if aggregation == AggregationMode.NO_AGGREGATION:
        group_legend = [i for i in name_subplot]
    else:
        group_legend = ["mentions" for _ in name_subplot]

    for poll in PollingOrganizations:
        if poll == PollingOrganizations.ALL:
            continue
        count += 1
        show_legend = True if (count == 1 or aggregation == AggregationMode.NO_AGGREGATION) else False

        df_poll = df[df["nom_institut"] == poll.value].copy() if poll != PollingOrganizations.ALL else df.copy()
        if df_poll.empty:
            continue
        nb_grades = len(get_grades(df_poll))
        colors = color_palette(palette="coolwarm", n_colors=nb_grades)
        color_dict = {f"intention_mention_{i + 1}": f"rgb{str(colors[i])}" for i in range(nb_grades)}

        col_intention = get_intentions_colheaders(df_poll, nb_grades)
        y_cumsum = df_poll[col_intention].to_numpy()
        for g, col, cur_y in zip(get_grades(df_poll), col_intention, y_cumsum.T):
            fig.add_trace(
                go.Scatter(
                    x=df_poll["fin_enquete"],
                    y=cur_y,
                    hoverinfo="x+y",
                    mode="lines",
                    line=dict(width=0.5, color=color_dict[col]),
                    stackgroup="one",  # define stack group
                    name=g,
                    showlegend=show_legend,
                    legendgroup=group_legend[count - 1],
                    legendgrouptitle_text=group_legend[count - 1],
                ),
                row=count,
                col=1,
            )

        for d in df_poll["fin_enquete"]:
            fig.add_vline(
                x=d,
                line_dash="dot",
                line_width=1,
                line_color="black",
                opacity=0.2,
                row=count,
                col=1,
            )

        fig.add_hline(
            y=50,
            line_dash="dot",
            line_width=2,
            line_color="black",
            annotation_text="50 %",
            annotation_position="bottom right",
            row=count,
            col=1,
        )
        fig.update_yaxes(title_text="Mentions (%)", tickfont_size=15, range=[0, 100], row=count, col=1)
        fig.update_xaxes(title_text="Mentions (%)", tickfont_size=15, range=[date_min, date_max], row=count, col=1)
    fig.update_layout(
        #     yaxis_range=(0, 100),
        width=600,
        height=800,
        plot_bgcolor="white",
        #     legend_title_text="Mentions",
        #     autosize=True,
        #     legend=dict(orientation="h", xanchor="center", x=0.5, y=-0.05),  # 50 % of the figure width/
    )

    # Title and detailed
    sponsor_str = ""
    date = df["fin_enquete"].max()
    title = (
        f"<b>Evolution des mentions au jugement majoritaire"
        + f"<br> pour le candidat {df.candidat.unique().tolist()[0]}</b>"
    )
    fig.update_layout(title=title, title_x=0.5)
    return fig


def add_image_to_fig(fig, x: float, y: float, sizex: float, sizey: float):
    fig.add_layout_image(
        dict(
            source="https://raw.githubusercontent.com/MieuxVoter/majority-judgment-tracker/main/icons/logo.png",
            xref="paper",
            yref="paper",
            x=x,
            y=y,
            sizex=sizex,
            sizey=sizey,
            xanchor="left",
            yanchor="bottom",
        )
    )
    return fig


def export_fig(fig, args, filename):
    if args.show:
        fig.show()
    if args.html:
        fig.write_html(f"{args.dest}/{filename}.html")
    if args.png:
        fig.write_image(f"{args.dest}/{filename}.png")
    if args.json:
        fig.write_json(f"{args.dest}/{filename}.json")
