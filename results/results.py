"""This script contains methods for reading the simulation results"""

import json
import warnings
import re
import ast

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from model.agents import *
from experiments.experiment import *

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
    return df


def plot_community_consumption_and_generation(results):
    realised_demand = extract_df_from_json(results, 'M1: realised_demand')
    total_generation = extract_df_from_json(results, 'M4: total_generation')

    df = pd.DataFrame()
    df['total_generation'] = total_generation.sum(axis=1)
    df['realised_demand'] = realised_demand.sum(axis=1)
    df['date'] = realised_demand.sum(axis=1).index.to_list()
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df.set_index('date', drop=True, inplace=True)

    fig, ax = plt.subplots(1, 1, figsize=(15, 5))
    sns.lineplot(data=df, ax=ax)
    ax.grid(True)
    plt.xticks(rotation=0)
    plt.legend()
    plt.title('Total electricity consumption and generation for the energy community')
    plt.xlabel('Date')
    plt.ylabel('kWh')
    plt.tight_layout()


def get_unique_levers_dict():
    """This function generates a dictionary of experiment result indexes having same lever combination i.e. same policy
    scenario"""
    # Get experiment conditions
    experiment_test = Experiment()
    experimental_conditions = experiment_test.prepare_experiment_setup()

    # Get unique levers
    levers_df = experimental_conditions.iloc[:, 3:]
    unique_levers = levers_df.drop_duplicates()

    # Collecting experiments having same lever combination i.e. same policy scenario
    same_levers = {}

    for i in range(len(unique_levers)):
        lever_combination_unique = unique_levers.iloc[i]
        same_levers[i] = []

        for j in range(len(levers_df)):
            lever_combination = levers_df.iloc[j]

            if lever_combination_unique.equals(other=lever_combination):
                same_levers[i].append(j)

    lever_descriptions = []
    for index, row in unique_levers.iterrows():
        l1 = get_lever_scenario(row['L1'], 'L1')
        l2 = get_lever_scenario(row['L2'], 'L2')
        l3 = get_lever_scenario(row['L3'], 'L3')
        lever_scenario = f"L1:{l1} L2:{l2} L3:{l3}"
        lever_descriptions.append(lever_scenario)

    unique_levers['lever information'] = lever_descriptions

    return same_levers, unique_levers


def get_lever_scenario(lever_value, lever):
    """reads lever values and returns policy scenario"""
    if lever == 'L1':
        if lever_value == 0:
            return 'B'
        elif lever_value == 5:
            return 'O'
        elif lever_value == 7.5:
            return 'V'
    elif lever == 'L2':
        if lever_value == 0.1:
            return 'B'
        elif lever_value == 0.5:
            return 'O'
        elif lever_value == 1:
            return 'V'
    elif lever == 'L3':
        if lever_value == 0.1:
            return 'B'
        elif lever_value == 0.5:
            return 'O'
        elif lever_value == 0.9:
            return 'V'


def load_results_from_csv(ec_name=None):
    """
    Loads the data of two pickles and returns them.
    :param ec_name: string name of energy community folder
    :param folder: string
    :return:
        results: dictionary with all results
    """
    mypath = os.getcwd() + '/' + ec_name + '/'
    outputs = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    all_results = {}

    for condition_output in outputs:
        path = f'{mypath}{condition_output}'
        df = pd.read_csv(path)

        condition_idx = re.findall(r'\d+', condition_output)
        condition_idx = condition_idx[0]
        # condition_idx = int(condition_output[22:-4])  # Takes only the number of the condition
        # condition_idx = int(condition_output[25:-4])  # Takes only the number of the condition
        all_results[condition_idx] = df

    return all_results


def separate_experiment_setups(results, number_of_steps):
    separated_results = {}

    for experiment, runs in results.items():
        separated_results[experiment] = []
        for run in range(number_of_simulation_runs):
            run_df = runs.iloc[:number_of_steps, :]
            runs = runs.iloc[number_of_steps + 1:, :]

            separated_results[experiment].append(run_df)

    return separated_results
