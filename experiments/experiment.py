"""
This module contains the Experiment class for performing experiments with the model.
"""
import itertools
import os
from os import listdir
from os.path import isfile, join

from model.model_code import *
from model.community_setup import *


class Experiment:
    """
    This class contains features and methods for performing experiments and data collection for results.
    """

    def __init__(self, uncertainty_values=None, policy_levers=None, agent_list=None, community=None):

        print('setting up the experiments...\n')
        self.start_time = time.time()
        self.all_results = None
        self.community = community
        self.agent_list = agent_list

        # Set up uncertainties
        if uncertainty_values is None:
            self.uncertainty_values = {"X1": [0.4, 0.8],
                                       # Minimum percentage of flexible demand available for demand response on a single
                                       # day (Social)
                                       "X2": [0.5, 1],
                                       # Maximum percentage of flexible demand available for demand response on a single
                                       # day (Social)
                                       "X3": [0.5, 0.9],
                                       # Percentage accuracy of day-ahead demand and  generation projections from
                                       # renewable assets (Technical)
                                       }
        else:
            self.uncertainty_values = uncertainty_values

        # Set up Policy Levers
        if policy_levers is None:
            self.policy_levers = {"L1": [0, 5, 7.5],
                                  # Percentage of members participating in the demand response program (Social)
                                  "L2": [0.1, 0.5, 1],
                                  # Percentage of flexible (shift-able)  demand for residential community members
                                  # (Technical)
                                  "L3": [0.1, 0.45, 0.9],
                                  # Percentage of flexible (shift-able)  demand for non-residential community members
                                  # (Technical)
                                  }
        else:
            self.policy_levers = policy_levers

        self.experiment_setup = self.prepare_experiment_setup()

    def prepare_experiment_setup(self):
        """Prepare experiment setup by creating combination of uncertainty and policy lever values"""
        dictionary = {**self.uncertainty_values, **self.policy_levers}
        columns = list(self.uncertainty_values.keys()) + list(self.policy_levers.keys())
        all_values = [dictionary[x] for x in columns]
        rows = list(itertools.product(*all_values))
        experiment_setup = pd.DataFrame(data=rows, columns=columns)
        return experiment_setup

    def run_experiments(self, number_of_replications=10, steps=365, number_of_segments=1, segment_index=0):
        """This function performs the experiment with all the parameters configured in the experiment set_up"""
        print('performing the experiments...\n')

        self.all_results = {}

        # For distributed computation, select conditions
        segment_borders = self.get_segment_borders(number_of_segments, segment_index)

        total_length = len(self.experiment_setup)
        segment_length = math.floor(total_length / number_of_segments)
        condition_index = 1

        for index, row in self.experiment_setup.iterrows():
            if segment_borders[0] <= index <= segment_borders[1]:
                if condition_index % 5 == 0:
                    print(f'Performing experiment condition {condition_index}/{segment_length}')
                condition_index += 1

                uncertainties = {'X1': row.loc['X1'],
                                 'X2': row.loc['X2'],
                                 'X3': row.loc['X3'],
                                 }

                levers = {'L1': row.loc['L1'],
                          'L2': row.loc['L1'],
                          'L3': row.loc['L1'],
                          }

                results_for_a_condition = None

                for _ in range(number_of_replications):
                    model = EnergyCommunity(levers=levers,
                                            uncertainties=uncertainties,
                                            agents_list=self.agent_list,
                                            start_date=None)
                    results = model.run_simulation(steps=steps, time_tracking=True)

                    data_frames = [results_for_a_condition, results]
                    results_for_a_condition = pd.concat(data_frames)

                self.all_results[index] = results_for_a_condition

        self.save_results()
        print('\n Experiment completed')

    def get_segment_borders(self, number_of_segments, segment_index):
        """
        Calculate the border indices of a segment for distributed computation.
        :param number_of_segments: number of segments for distri buted computation.
        :param segment_index: which segment to execute,starting from 0
        :return: tuple: start and end index of the segment
        """
        total_length = len(self.experiment_setup)
        segment_length = math.floor(total_length / number_of_segments)
        start_index = segment_index * segment_length
        end_index = start_index + (segment_length - 1)
        borders = (start_index, end_index)

        return borders

    def save_results(self, folder='./output/'):
        """Save the results of the experiment in a csv file"""
        print('Saving results...\n')

        for condition_index, results_df in self.all_results.items():
            path = f'{folder}_{self.community}_results_{condition_index}.csv'
            results_df.to_csv(path)

    @staticmethod
    def load_results(folder='./output/', ec_name=None):
        """
        Loads the data of two pickles and returns them.
        :param ec_name: string name of energy community folder
        :param folder: string
        :return:
            results: dictionary with all results
        """
        folder = folder + ec_name + '/'
        mypath = os.getcwd() + '/output/' + ec_name + '/'
        outputs = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        all_results = {}

        for condition_output in outputs:
            path = f'{folder}{condition_output}'
            df = pd.read_csv(path)

            # condition_idx = int(condition_output[22:-4])  # Takes only the number of the condition
            condition_idx = int(condition_output[25:-4])  # Takes only the number of the condition
            all_results[condition_idx] = df

        return all_results


if __name__ == '__main__':
    start_time = time.time()

    community_name = 'gridflex_heeten'
    agents = create_community_configuration(community_name=community_name)
    experiment = Experiment(agent_list=agents, community=community_name)
    experiment.run_experiments(number_of_replications=10, steps=365, number_of_segments=6, segment_index=5)

    run_time = round(time.time() - start_time, 2)
    print(f'Run time: {run_time} seconds')
