"""This script contains methods for reading the simulation results"""

import json
import warnings
import re
import ast

import matplotlib.pyplot as plt
import pandas as pd

from model.agents import *

warnings.filterwarnings("ignore")


def extract_results(data, column, agent_list):
    """Extracts the results from the dataframe and returns a DataFrame of the results
    :type data: DaraFrame
    :type column: str
    :type agent_list: list
    """
    columns = pd.date_range(start='2021/01/01', periods=96, freq='15min').strftime('%H:%M:%S').to_list()
    df = pd.DataFrame(columns=columns + ['agent_type'])
    agent_name_dict = get_agent_name_dict(agent_list)
    for agent_type in agent_list:
        for index, row in data.iterrows():
            item = json.loads(row[column])[str(agent_type)]
            a_series = pd.Series(item, index=columns)
            a_type = pd.Series([agent_name_dict[agent_type]], index=['agent_type'])
            a_series = pd.concat([a_series, a_type], axis=0)
        df = df.append(a_series, ignore_index=True)
    df = format_df(df)
    return df


def format_df(df):
    df = df.T
    header_row = -1
    df.columns = df.iloc[header_row]
    df = df.iloc[:-1, :]
    # df = df.reset_index(drop=True)
    return df


def get_agent_name_dict(agent_list):
    dict_vessel = {}
    for agent in agent_list:
        item = str(agent).split('.')[-1].strip("'>")
        dict_vessel[agent] = item
    return dict_vessel


def plot_results(df, stacked=True, kind='bar', plt_title=''):
    """

    :param df: DataFrame
    :param stacked: str
    :param kind: str
    :type plt_title: str
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    df.plot(kind=kind, stacked=stacked, ax=ax)
    plt.xlabel('Hours')
    plt.ylabel('kWh')
    plt.title(plt_title.upper())
    plt.tight_layout()


def extract_df_from_json(results, column='savings'):
    """
    Extract the data from result files
    :param results: DataFrame returned by the model
    :param column: Name of column for extracting the DataFrame
    :return: DataFrame with agents and value of matrix for each timestep
    """
    df = pd.DataFrame()
    for index, row in results.iterrows():
        try:
            json.loads(row[column])
        except ValueError:
            item = row[column]
            item = ast.literal_eval(re.search('({.+})', item).group(0))
        else:
            item = json.loads(row[column])

        df = df.append(item, ignore_index=True)
    df = df[1:]
    df['date'] = results['date']
    df = df.set_index('date')
    return df


