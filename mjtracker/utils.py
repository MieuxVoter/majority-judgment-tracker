from pandas import DataFrame


def get_list_survey(df: DataFrame):
    """
    Get the list of surveys id in the DataFrame

    Parameters
    ----------
    df : DataFrame
        DataFrame containing the surveys
    Returns
    -------
        List of surveys id
    """
    return df["id"].unique()


def get_intentions(df: DataFrame, nb_mentions: int = 7) -> object:
    """
    Get the intentions of voters

    Parameters
    ----------
    df : DataFrame
        DataFrame containing the survey
    nb_mentions : int
        Number of mentions
    Returns
    -------
        Dataframe surveys with intentions of voters only
    """
    colheader = ["candidat"]
    colheader.extend(get_intentions_colheaders(df, nb_mentions))
    return df[colheader]


def get_intentions_colheaders(df: DataFrame, nb_mentions: int = 7):
    """
    Get the colheaders of the intentions of votes

    Parameters
    ----------
    df : DataFrame
       DataFrame containing the surveys
    nb_mentions : int
       Number of mentions
    Returns
    -------
       List of colheaders of the intentions of votes
    """
    list_col = df.columns.to_list()
    intentions_colheader = [s for s in list_col if "intention" in s]
    return intentions_colheader[:nb_mentions]


def get_grades(df: DataFrame, nb_mentions: int = 7) -> list:
    """
    Get the grades of the candidates

    Parameters
    ----------
    df : DataFrame
       DataFrame containing the surveys
    nb_mentions : int
       Number of mentions
    Returns
    -------
       List of grades of the candidates
    """
    list_col = df.columns.to_list()
    mentions_colheader = [s for s in list_col if "mention" in s and not "intention" in s and not "nombre" in s]
    mentions_colheader = mentions_colheader[:nb_mentions]
    numpy_mention = df[mentions_colheader].to_numpy().tolist()[0]

    numpy_mention = [m for m in numpy_mention if m != "nan"]
    return numpy_mention


def get_candidates(df: DataFrame):
    """
    Get the list of candidates

    Parameters
    ----------
    df : DataFrame
        DataFrame containing the surveys
    Returns
    -------
        List of candidates
    """
    return df["candidat"].unique()


def rank2str(rank: int):
    """
    Convert a rank to a string from a int

    Parameters
    ----------
    rank : int
        Rank of the candidate
    Returns
    -------
        String of the rank
    """
    if rank == 1:
        return f"{rank}er"
    else:
        return f"{rank}e"
