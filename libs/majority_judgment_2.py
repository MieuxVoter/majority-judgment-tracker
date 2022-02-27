#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 23:34:39 2022

@author: Rémy Poulain
adapted by Pierre Puchaud 10 Fev 2022
"""

import matplotlib.pyplot as plt
import numpy as np
import csv

from matplotlib.lines import Line2D
import matplotlib.patches as patches
import os

from typing import Dict, List, Union


def majority_judgment(data: Dict[str, List[Union[int, float]]] = None, reverse: bool = False):
    """
    apply majority judgment

    Parameters
    ----------
    data: Dict[str, List[Union[int, float]]
        Results of the votes
        str correspond to the names of candidates, List of int is the number for each grades
    reverse: bool
        if you want to flip the grades order
    Returns
    -------
        Rank order for each candidates in a Dictionary Dict[str,rank: int]
    """
    if reverse:
        data = {x: l[::-1] for x, l in data.items()}
    snbvot = {round(sum(x), 2) for x in data.values()}
    total_votes = list(snbvot)[0]
    if not len(snbvot) == 1:
        raise ValueError("note the same number of vote for each candidate")

    cumulative_sum = {x: np.cumsum(y) / total_votes for x, y in data.items()}

    # compute median indexes
    median_grades = {x: best_grade(l) for x, l in cumulative_sum.items()}
    # best one
    best_grade_mm = sorted(median_grades.values())[-1]

    majority = {x: fmajorit(median_grades, total_votes, x, r) for x, r in data.items()}
    bests = sorted(majority.items(), key=lambda x: x[1][1])[::-1]

    # as written by Fabre in fact it is just necessary to compare the modified note
    ranking = {x[0]: i + 1 for i, x in enumerate(bests)}

    return ranking


def best_grade(l: List):
    """
    Evaluates the best grades

    Parameters
    ----------
    l: List
        The list of the cumulative sum from 0 to 1
    Returns
    -------
    The median grade
    """
    for i, x in enumerate(l):
        if x > 0.5:  # todo: ici ça peut être >= , need to handle pair and not pair cases.
            return i


def fmajorit(index_median: Dict[str, int], nbvot: int, candidate: str, grades: List[int]):
    """
    Rank each candidate according to
    # https://fr.wikipedia.org/wiki/M%C3%A9thode_de_meilleure_m%C3%A9diane#cite_note-Fabre20-3

    Parameters
    ----------
    index_median: Dict[str, int]
        The dictionary of candidate and its median grade
    nbvot: int
        The total number of votes
    candidate: str
        The considered candidate
    grades: List[int]
        The list number of grades for the given candidat

    Returns
    -------
    A list which contains
    i: alpha the index corresponding to the majority grade
    m: "enhanced" grade
    p: rate of sponsors, size at the left
    q: rate of opponents, size at the right
    b: boolean = True if more sponsors than opponents
    d: bonus / malus function of p and q
    e: the number of votes to pass to get the next grade
    i2: index of the next grade
    """
    i = index_median[candidate]
    q = sum(grades[:i]) / nbvot
    p = sum(grades[i + 1 :]) / nbvot
    b = p > q
    m = i
    if b:
        d = p
        i2 = i + 1
    else:
        d = -q
        i2 = i - 1
    m += d
    e = min(nbvot / 2 + 1 - sum(grades[:i]), sum(grades[: (i + 1)]) - (nbvot / 2))
    e = int(e * 2)

    return [i, m, p, q, b, d, e, i2]


def scoring(index_median: Dict[str, int], nbvot: int, candidate: str, grades: List[int]):
    """
    rank using the method writen in the 'La recherche' from 2012 and add some elements to the precedent method
    score is a ranking going from 10 to 91 (in the case of 7 mentions)
    Parameters
    ----------
    index_median: Dict[str, int]
        The dictionary of candidate and its median grade
    nbvot: int
        The total number of votes
    candidate: str
        The considered candidate
    grades: List[int]
        The list number of grades for the given candidat

    Returns
    -------
        Score
    """

    i = index_median[candidate]

    prc = list(grades)

    for nb, val in enumerate(prc):
        prc[nb] = 100 * val / nbvot

    sum1 = 0
    sum2 = 0
    bonus = 0
    for nb, val in enumerate(prc):
        if nb < i:
            sum1 += val
        elif nb > i:
            sum2 += val
    if sum1 == sum2:
        bonus = 1
    elif sum1 < sum2:
        bonus = 2
    if bonus == 2:
        ballotage = sum2 / 100
    else:
        ballotage = (100 - sum1) / 100
    score = (i + 1) * 10 + bonus + ballotage

    return score