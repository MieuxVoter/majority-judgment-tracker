#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 15:10:01 2022

@author: sballe
"""
import pandas as pd
import sqlite3
import os


def normalize_file(
    file: str, sans_op_mode: str = "Insuffisant", aggregat: bool = False, aggregate_method: str = "unkown yet"
):
    #    pd.set_option('display.max_rows', 20)
    #    pd.set_option('display.max_columns', 100)
    #    pd.set_option('display.width', 10000)
    #    pd.set_option('display.max_colwidth', 10)
    try:
        os.remove("jmajo.sqlite")
    except OSError as error:
        print("sqlite file was not existing")
    con = sqlite3.connect("jmajo.sqlite")
    #    con.set_trace_callback(print)
    sql = con.cursor()

    # parametres de données
    #    sans_op_mode='Insuffisant'
    #    sans_op_mode='Insuffisant B'
    #    sans_op_mode='Passable'
    #    sans_op_mode='Passable B'
    #    sans_op_mode='Assez bien'
    #    sans_op_mode='Assez bien B'

    #    aggregat=False
    #    agrregat_mode="todo"

    # normalisation de la base

    df = pd.read_csv(file, na_filter=False)
    df.to_sql("sondages", con, if_exists="append", index=False)
    df = pd.read_csv("standardisation.csv", na_filter=False)
    df.to_sql("standardisation", con, if_exists="append", index=False)

    sql.execute(
        """
                create table sondages_standard(
                    candidat	,
                    parti,
                    candidat_presidentielle,
                    nombre_mentions,
                    mention_1,
                    mention_2,
                    mention_3,
                    mention_4,
                    mention_5,
                    mention_6,
                    mention_7,
                    intention_mention_1 float,
                    intention_mention_2 float,
                    intention_mention_3 float,
                    intention_mention_4 float,
                    intention_mention_5 float,
                    intention_mention_6 float,
                    intention_mention_7 float,
                    id,
                    nom_institut,
                    commanditaire,
                    debut_enquete,
                    fin_enquete,
                    echantillon float,
                    population,
                    hypothese
                )
                """
    )

    sql.execute(
        """
                create table sondages_aggrege(
                    candidat	,
                    parti,
                    candidat_presidentielle,
                    nombre_mentions,
                    mention_1,
                    mention_2,
                    mention_3,
                    mention_4,
                    mention_5,
                    mention_6,
                    mention_7,
                    intention_mention_1 float,
                    intention_mention_2 float,
                    intention_mention_3 float,
                    intention_mention_4 float,
                    intention_mention_5 float,
                    intention_mention_6 float,
                    intention_mention_7 float,
                    id,
                    nom_institut,
                    commanditaire,
                    debut_enquete,
                    fin_enquete,
                    echantillon float,
                    population,
                    hypothese
                )
                """
    )

    sql_query = pd.read_sql_query(
        """
                                   SELECT
                                   mention_1,
                                   mention_2,
                                   mention_3,
                                   mention_4,
                                   mention_5,
                                   mention_6,
                                   mention_7,
                                   mention_1_out,
                                   mention_2_out,
                                   mention_3_out,
                                   mention_4_out,
                                   mention_5_out,
                                   mention_6_out,
                                   mention_7_out
                                   FROM standardisation
                                   where sans_op_mode='%s'
                                   """
        % sans_op_mode,
        con,
    )

    df = pd.DataFrame(sql_query)
    for row in df.itertuples():
        sql_str = """
                insert into sondages_standard(
                        candidat,
                        parti,
                        candidat_presidentielle,
                        nombre_mentions,
                        mention_1,
                        mention_2,
                        mention_3,
                        mention_4,
                        mention_5,
                        mention_6,
                        mention_7,
                        intention_mention_1,
                        intention_mention_2,
                        intention_mention_3,
                        intention_mention_4,
                        intention_mention_5,
                        intention_mention_6,
                        intention_mention_7,
                        id,
                        nom_institut,
                        commanditaire,
                        debut_enquete,
                        fin_enquete,
                        echantillon,
                        population,
                        hypothese
                    )
                    select 
                        candidat	,
                        parti,
                        candidat_presidentielle,
                        7 as nombre_mentions,
                        'Excellent' mention_1,
                        'Très bien' mention_2,
                        'Bien' mention_3,
                        'Assez bien' mention_4,
                        'Passable' mention_5,
                        'Insuffisant' mention_6,
                        'A rejeter'  mention_7,
                        1.0*echantillon*(%s) as intention_mention_1,
                        1.0*echantillon*(%s) as intention_mention_2,
                        1.0*echantillon*(%s) as intention_mention_3,
                        1.0*echantillon*(%s) as intention_mention_4,
                        1.0*echantillon*(%s) as intention_mention_5,
                        1.0*echantillon*(%s) as intention_mention_6,
                        1.0*echantillon*(%s) as intention_mention_7,
                        id,
                        nom_institut,
                        commanditaire,
                        debut_enquete,
                        fin_enquete,
                        echantillon,
                        population,
                        hypothese
                     from sondages so
                     where so.mention_1=? 
                         and so.mention_2=? 
                         and so.mention_3=? 
                         and so.mention_4=? 
                         and so.mention_5=? 
                         and so.mention_6=? 
                         and so.mention_7=?
                    """
        sql.execute(
            sql_str
            % (
                row.mention_1_out,
                row.mention_2_out,
                row.mention_3_out,
                row.mention_4_out,
                row.mention_5_out,
                row.mention_6_out,
                row.mention_7_out,
            ),
            (
                str(row.mention_1 or ""),
                str(row.mention_2 or ""),
                str(row.mention_3 or ""),
                str(row.mention_4 or ""),
                str(row.mention_5 or ""),
                str(row.mention_6 or ""),
                str(row.mention_7 or ""),
            ),
        )
        con.commit()

    if aggregat:
        # todo les aggregats, en vérifiant quels sondages sont compatibles rapport nombre de candidats (restreindre à la portion de candidats communs dans les sondages ?)
        # note, on perd des éléments en passant en aggrégat
        sql_str = """
                insert into sondages_aggrege(
                        candidat,
                        parti,
                        candidat_presidentielle,
                        nombre_mentions,
                        mention_1,
                        mention_2,
                        mention_3,
                        mention_4,
                        mention_5,
                        mention_6,
                        mention_7,
                        intention_mention_1,
                        intention_mention_2,
                        intention_mention_3,
                        intention_mention_4,
                        intention_mention_5,
                        intention_mention_6,
                        intention_mention_7,
                        id,
                        nom_institut,
                        commanditaire,
                        debut_enquete,
                        fin_enquete,
                        echantillon,
                        population,
                        hypothese
                    )
                select 
                        candidat,
                        parti,
                        candidat_presidentielle,
                        nombre_mentions,
                        mention_1,
                        mention_2,
                        mention_3,
                        mention_4,
                        mention_5,
                        mention_6,
                        mention_7,
                        round(intention_mention_1/echantillon,2),
                        round(intention_mention_2/echantillon,2),
                        round(intention_mention_3/echantillon,2),
                        round(intention_mention_4/echantillon,2),
                        round(intention_mention_5/echantillon,2),
                        round(intention_mention_6/echantillon,2),
                        round(intention_mention_7/echantillon,2),
                        id,
                        '' as nom_institut,
                        '' as commanditaire,
                        '1900-01-01' as debut_enquete,
                        '1900-01-01' as fin_enquete,
                        echantillon,
                        '' as population,
                        '' as hypothese
                from sondages_standard
                """
    else:
        sql_str = """
                insert into sondages_aggrege(
                        candidat,
                        parti,
                        candidat_presidentielle,
                        nombre_mentions,
                        mention_1,
                        mention_2,
                        mention_3,
                        mention_4,
                        mention_5,
                        mention_6,
                        mention_7,
                        intention_mention_1,
                        intention_mention_2,
                        intention_mention_3,
                        intention_mention_4,
                        intention_mention_5,
                        intention_mention_6,
                        intention_mention_7,
                        id,
                        nom_institut,
                        commanditaire,
                        debut_enquete,
                        fin_enquete,
                        echantillon,
                        population,
                        hypothese
                    )
                select 
                        candidat,
                        parti,
                        candidat_presidentielle,
                        nombre_mentions,
                        mention_1,
                        mention_2,
                        mention_3,
                        mention_4,
                        mention_5,
                        mention_6,
                        mention_7,
                        round(intention_mention_1/echantillon,2),
                        round(intention_mention_2/echantillon,2),
                        round(intention_mention_3/echantillon,2),
                        round(intention_mention_4/echantillon,2),
                        round(intention_mention_5/echantillon,2),
                        round(intention_mention_6/echantillon,2),
                        round(intention_mention_7/echantillon,2),
                        id,
                        nom_institut,
                        commanditaire,
                        debut_enquete,
                        fin_enquete,
                        echantillon,
                        population,
                        hypothese
                from sondages_standard
                """

    sql.execute(sql_str)
    con.commit()
    # to avoid rounding issues on some conversion to standard 7 mentions while working in percentage.
    sql_str = "update sondages_aggrege set intention_mention_4=round(100.0-intention_mention_1-intention_mention_2-intention_mention_3-intention_mention_5-intention_mention_6-intention_mention_7,2)"
    sql.execute(sql_str)
    con.commit()
    sql_query = pd.read_sql_query("select * from sondages_aggrege", con)
    df = pd.DataFrame(sql_query)
    con.close()
    return df
