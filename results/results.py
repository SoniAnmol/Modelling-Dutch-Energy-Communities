"""This script contains methods for reading the simulation results"""

import json
import warnings
import re
import ast

import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import pandas as pd

from model.agents import *
from experiments.experiment import *

warnings.filterwarnings("ignore")


def extract_from_json(item):
    """
    Extract the data from json file
    :param item: matrix stored in the dataframe
    :return: Dict
    """
    try:
        json.loads(item)
    except ValueError:
        item = ast.literal_eval(re.search('({.+})', item).group(0))
    else:
        item = json.loads(item)
    return item


def create_results_df(results):
    """
    Returns a single dataframe of results from all experiment setups
    @param results: Dict
    @return df: DataFrame
    """
    d = {}
    for key in tqdm(results.keys()):
        d = d | results[key].to_dict(orient='index')
    print(f"Creating dataframe...")
    df = pd.DataFrame.from_dict(d, orient='index')
    return df


def extract_df_from_json(results, column='savings'):
    """
    Extract the data from json result files
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


def calculate_key_matrices(df):
    """" Returns total, total_residential, mean_residential , total_non_residential value for 'M1: realised_demand',
    'M2: scheduled_demand', 'M3: shifted_load', 'M5: savings_on_ToD', and 'M6: energy_costs'.
        @param df: DataFrame
        @return result_matrices: Dict
    """

    # create a list of matrix
    matrices = ['M1: realised_demand', 'M2: scheduled_demand', 'M3: shifted_load',
                'M5: savings_on_ToD', 'M6: energy_costs']
    # create a dictionary of columns header and its index
    columns_dict = {}
    index = 1
    columns = df.columns.to_list()

    for header in columns:
        columns_dict[header] = index
        index += 1

    # get list of residential and non-residential members
    m = df.loc[0, 'M1: realised_demand']
    m = extract_from_json(item=m)
    members = list(m.keys())
    check = 'hh'
    residential = [idx for idx in members if idx.lower().startswith(check.lower())]
    non_residential = list(set(members) - set(residential))

    print(f"calculating total, total_residential, mean_residential , total_non_residential value for {matrices}...")
    result_matrices = {}
    # iterate over results dataframe
    for row in tqdm(df.itertuples(), total=len(df)):
        result_dict = {}
        # iterate over performance matrix
        for matrix in matrices:
            m = extract_from_json(item=row[columns_dict[matrix]])
            # calculate important values from the matrix
            result_dict[f"{matrix[:2]}_total"] = sum(m.values())
            result_dict[f"{matrix[:2]}_total_residential"] = sum({k: m[k] for k in m.keys() & residential}.values())
            result_dict[f"{matrix[:2]}_mean_residential"] = sum(
                {k: m[k] for k in m.keys() & residential}.values()) / len(residential)
            result_dict[f"{matrix[:2]}_total_non_residential"] = sum(
                {k: m[k] for k in m.keys() & non_residential}.values())
        # set index for dictionary
        result_matrices[row[0]] = result_dict
    return result_matrices


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
    """This function generates a dictionary of experiment result indexes having same lever combination i.e. same Policies"""
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


def get_lever_description(lever_value, lever):
    """
    Reads lever values and returns lever description
    @param lever_value: Float
    @param lever: String
    @return: String, String
    """
    if lever == 'L1':
        if lever_value == 0:
            return 'Participation in demand response 0%', 'B'
        elif lever_value == 0.5:
            return 'Participation in demand response 50%', 'O'
        elif lever_value == 0.75:
            return 'Participation in demand response 75%', 'V'
    elif lever == 'L2':
        if lever_value == 0.1:
            return 'Residential flexible demand 10%', 'B'
        elif lever_value == 0.5:
            return 'Residential flexible demand 50%', 'O'
        elif lever_value == 1:
            return 'Residential flexible demand 100%', 'V'
    elif lever == 'L3':
        if lever_value == 0.1:
            return 'Non-residential flexible demand 10%', 'B'
        elif lever_value == 0.45:
            return 'Non-residential flexible demand 45%', 'O'
        elif lever_value == 0.9:
            return 'Non-residential flexible demand 90%', 'V'


def get_lever_scenario(lever_value, lever):
    """Reads lever values and returns policy scenario for subplot titles"""
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
        elif lever_value == 0.45:
            return 'O'
        elif lever_value == 0.9:
            return 'V'


def get_uncertainty_description(uncertainty_value, uncertainty_parameter):
    """
    Reads uncertainty value and parameter name to return scenario
    @param uncertainty_value: Float
    @param uncertainty_parameter: String
    @return: String, String
    """
    if uncertainty_parameter == 'X1':
        if uncertainty_value == 0.4:
            return 'Availability of min. flexible demand 40%', 'N'
        else:
            return 'Availability of min. flexible demand 80%', 'O'
    elif uncertainty_parameter == 'X2':
        if uncertainty_value == 0.5:
            return 'Availability of max.flexible demand 50%', 'N'
        else:
            return 'Availability of max. flexible demand 100%', 'O'
    elif uncertainty_parameter == 'X3':
        if uncertainty_value == 0.5:
            return 'Accuracy of demand response schedule 50%', 'N'
        else:
            return 'Accuracy of demand response schedule 90%', 'O'


def load_results_from_csv(ec_name=None):
    """
    Loads the data from all csv. files and returns a dictionary.
    :param ec_name: string name of energy community folder
    :param folder: string
    :return:
        results: dictionary with all results
    """
    mypath = os.getcwd() + '/' + 'data/raw/' + ec_name + '/'
    outputs = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    all_results = {}

    for condition_output in outputs:
        path = f'{mypath}{condition_output}'
        df = pd.read_csv(path)

        condition_idx = re.findall(r'\d+', condition_output)  # Extract experiment setup number from file name
        condition_idx = condition_idx[0]  # Takes only the number of the condition
        all_results[condition_idx] = df

    return all_results


def separate_experiment_setups(results, number_of_steps=365, number_of_simulation_runs=10):
    """
    Reads experiment results and returns a dictionary of results with experiment setup as key.
    """
    separated_results = {}

    for experiment, runs in results.items():
        separated_results[experiment] = []
        for run in range(number_of_simulation_runs):
            run_df = runs.iloc[:number_of_steps, :]
            runs = runs.iloc[number_of_steps + 1:, :]

            separated_results[experiment].append(run_df)

    return separated_results


def add_experiment_setup_details(results):
    """
    Adds experiment parameter information to the results dataframe
    @param results: DataFrame
    @return: Dict
    """

    experiment_test = Experiment()
    experimental_conditions = experiment_test.prepare_experiment_setup()
    model_inputs = experimental_conditions.columns.to_list()
    counter = 0
    print("starting the iteration through results...")
    for key, row in tqdm(experimental_conditions.iterrows(), total=len(experimental_conditions)):
        df = results[str(key)]
        # assign input parameters to dataframe
        policy_description = ''
        policy = ''
        scenario_description = ''
        scenario = ''
        for model_input in model_inputs:
            df[model_input] = row[model_input]
            # If input parameter is a lever, get the unique policy
            if model_input in ['L1', 'L2', 'L3']:
                lever_description, lever = get_lever_description(row[model_input], model_input)
                policy = policy + f"{model_input} :{lever} "
                policy_description = policy_description + f"{lever_description}\n"
            # If input parameter is an uncertainty, get unique scenario
            elif model_input in ['X1', 'X2', 'X3']:
                uncertainty_description, uncertainty = get_uncertainty_description(row[model_input], model_input)
                scenario = scenario + f"{model_input} :{uncertainty} "
                scenario_description = scenario_description + f"{uncertainty_description}\n"
        # assign experiment setup
        df['experiment_setup'] = key
        # assign scenario and policy
        df['scenario_description'] = scenario_description
        df['policy_description'] = policy_description
        df['scenario'] = scenario
        df['policy'] = policy
        # rename column
        df.rename(columns={'Unnamed: 0': 'step'}, inplace=True)
        # set date column
        df['date'] = pd.date_range(start='01-01-2021', freq='D', periods=365).strftime('%d-%m-%Y').to_list() * 10
        df['index'] = np.arange(counter, counter + len(df))
        counter = counter + len(df)
        df.set_index('index', inplace=True, drop=True)

        # store the formatted dataframe in the dictionary
        results[str(key)] = df

    return results


def combine_dictionaries(results):
    """Combine results from different simulation runs into one dictionary"""
    d = {}
    for key in tqdm(results.keys()):
        d = d | results[key].to_dict(orient='index')
    return d


def get_members_list(d):
    """Returns a list of all members in the dictionary, residential and non-residential members"""
    members = list(extract_from_json(d[0]['M1: realised_demand']).keys())
    check = 'hh'
    residential = [idx for idx in members if idx.lower().startswith(check.lower())]
    non_residential = list(set(members) - set(residential))
    check = 'hh1'
    hh1 = [idx for idx in members if idx.lower().startswith(check.lower())]
    check = 'hh2'
    hh2 = [idx for idx in members if idx.lower().startswith(check.lower())]
    check = 'hh3'
    hh3 = [idx for idx in members if idx.lower().startswith(check.lower())]
    residential_types = {'hh1': hh1, 'hh2': hh2, 'hh3': hh3}
    return residential, non_residential, residential_types


def extract_important_results(d):
    """Extracts important results from the dictionary"""
    columns = ['step', 'date', 'X1', 'X2', 'X3', 'L1', 'L2', 'L3', 'experiment_setup', 'scenario_description',
               'policy_description', 'scenario', 'policy', 'M1_total', 'M1_total_residential', 'M1_mean_residential',
               'M1_total_non_residential', 'M2_total', 'M2_total_residential', 'M2_mean_residential',
               'M2_total_non_residential', 'M3_total', 'M3_total_residential', 'M3_mean_residential',
               'M3_total_non_residential', 'M4_total', 'M5_total', 'M5_total_residential',
               'M5_mean_residential', 'M5_total_non_residential', 'M6_total', 'M6_total_residential',
               'M6_mean_residential', 'M6_total_non_residential']
    # create list of residential and non-residential members
    residential, non_residential, residential_types = get_members_list(d)
    matrices = ['M1: realised_demand', 'M2: scheduled_demand', 'M3: shifted_load', 'M5: savings_on_ToD',
                'M6: energy_costs']
    for key in tqdm(d.keys()):
        for matrix in matrices:
            m = extract_from_json(d[key][matrix])
            d[key][f"{matrix[:2]}_total"] = sum(m.values())
            d[key][f"{matrix[:2]}_total_residential"] = sum({k: m[k] for k in m.keys() & residential}.values())
            d[key][f"{matrix[:2]}_mean_residential"] = sum(
                {k: m[k] for k in m.keys() & residential}.values()) / len(residential)
            d[key][f"{matrix[:2]}_std_residential"] = np.std(list({k: m[k] for k in m.keys() & residential}.values()))
            d[key][f"{matrix[:2]}_total_non_residential"] = sum(
                {k: m[k] for k in m.keys() & non_residential}.values())
            for residential_type in residential_types.keys():
                d[key][f"{matrix[:2]}_mean_{residential_type}"] = sum(
                    {k: m[k] for k in m.keys() & residential_types[residential_type]}.values()) / len(
                    residential_types[residential_type])
        d[key]["M4_total"] = extract_from_json(d[key]['M4: total_generation'])["<class 'model.agents.Solar'>"]
        d[key] = {k: d[key][k] for k in d[key].keys() & columns}

    return d


def check_data_sanity(results):
    """Check if data is sane"""
    columns = results.select_dtypes(include=['float64']).columns.to_list()
    for column in columns:
        results.loc[results[column] < 0, column] = 0
    return results


def aggregate_timeseries_data(results):
    """"
    Aggregate timeseries data
    @param results: results dataframe
    @return: aggregated dataframe
    """
    sum_c = ['M1_total_residential', 'M1_total_non_residential', 'M1_total',
             'M2_total_residential', 'M2_total_non_residential', 'M2_total',
             'M3_total_residential', 'M3_total_non_residential', 'M3_total',
             'M4_total',
             'M5_total_residential', 'M5_total_non_residential', 'M5_total',
             'M6_total_residential', 'M6_total_non_residential', 'M6_total', ]
    mean_c = ['M1_mean_residential',
              'M2_mean_residential',
              'M3_mean_residential',
              'M5_mean_residential',
              'M6_mean_residential', ]

    experiment_setups = results['experiment_setup'].unique()
    # Aggregate annual values
    results_dict = {}
    for experiment_setup in tqdm(experiment_setups):
        replications = results[results['experiment_setup'] == experiment_setup]
        mean_values = replications.groupby('date').mean()
        sum_dict = mean_values[sum_c].sum().to_dict()
        mean_dict = mean_values[mean_c].mean().to_dict()
        results_dict[experiment_setup] = {**sum_dict, **mean_dict, 'experiment_setup': experiment_setup} | \
                                         mean_values.loc[
                                             '01-01-2021', ['X1', 'X2', 'X3', 'L1', 'L2', 'L3']].to_dict()

    annual_df = pd.DataFrame.from_dict(results_dict, orient='index')
    return annual_df
