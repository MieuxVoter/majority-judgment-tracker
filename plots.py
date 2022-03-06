from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from seaborn import color_palette
from pandas import DataFrame
from utils import get_intentions_colheaders, get_candidates


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

    # Add sans opinion to y tick label # todo : it may be simplified !

    if show_no_opinion:
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

    # xticks
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

    fig.add_layout_image(
        dict(
            source="https://raw.githubusercontent.com/MieuxVoter/majority-judgment-tracker/main/icons/logo.png",
            xref="paper",
            yref="paper",
            x=0.8,
            y=0.95,
            sizex=0.2,
            sizey=0.2,
            xanchor="left",
            yanchor="bottom",
        )
    )

    return fig


def ranking_plot(
    df, source: str = None, sponsor: str = None, show_best_grade: bool = True, show_no_opinion: bool = True
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

    fig = go.Figure()

    df = df.sort_values(by="fin_enquete")
    annotations = []
    for ii in get_candidates(df):
        print(ii)
        temp_df = df[df["candidat"] == ii]
        fig.add_trace(
            go.Scatter(
                x=temp_df["fin_enquete"],
                y=temp_df["rang"],
                mode="lines",
                name=ii,
                marker=dict(color=COLORS[ii]["couleur"]),
                legendgroup=ii,
            )
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
            )
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
            )
        )

        # name with break btw name and surname
        idx_space = ii.find(" ")
        name_label = ii[:idx_space] + "<br>" + ii[idx_space + 1 :]
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
                )
            )

        extended_name_label = f"<b>{name_label}</b>"
        if show_best_grade:
            extended_name_label += (
                "<br>"
                + temp_df["mention_majoritaire"].iloc[-1][0].upper()
                + temp_df["mention_majoritaire"].iloc[-1][1:]
            )
        if show_no_opinion:
            extended_name_label += "<br><i>(sans opinion " + str(temp_df["sans_opinion"].iloc[-1]) + "%) </i>"

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
            ),
        )

    fig.add_vline(x="2022-04-10", line_dash="dot")
    annotations.append(
        dict(
            x="2022-04-10",
            y=1.5,
            xanchor="left",
            xshift=10,
            yanchor="middle",
            text="1er Tour",
            font=dict(family="Arial", size=size_annotations),
            showarrow=False,
        )
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed", tick0=1, dtick=1, visible=False),
        annotations=annotations,
        plot_bgcolor="white",
        showlegend=False,
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

    fig.add_layout_image(
        dict(
            source="https://raw.githubusercontent.com/MieuxVoter/majority-judgment-tracker/main/icons/logo.png",
            xref="paper",
            yref="paper",
            x=0.05,
            y=1.01,
            sizex=0.15,
            sizey=0.15,
            xanchor="left",
            yanchor="bottom",
        )
    )

    return fig
