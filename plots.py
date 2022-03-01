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
):
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
        width=1000,
        height=600,
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
        legend=dict(orientation="h", xanchor="center", x=0.5, y=-0.05),  # 50 % of the figure width
    )

    fig.update(data=[{"hovertemplate": "Intention: %{x}<br>Candidat: %{y}"}])
    # todo: need to plot grades in hovertemplate.

    # no back ground
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

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


def ranking_plot(df):
    df = df[df["fin_enquete"] > "2021-12-01"]
    fig = go.Figure()
    for ii in get_candidates(df):
        temp_df = df[df["candidat"] == ii]
        fig.add_trace(go.Scatter(x=temp_df["fin_enquete"], y=temp_df["rang"]))

    print("yo")
    fig.show()
    return fig
