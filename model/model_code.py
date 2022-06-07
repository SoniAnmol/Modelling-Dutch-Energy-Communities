# import datetime
import time

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

from model.community_setup import *
from model.data_reporters import *

agent_list = generate_agent_list()


class EnergyCommunity(Model):
    """A model with some number of agents."""

    date = None

    def __init__(self, agents_list=agent_list, time_of_day=1, start_date=None):
        super().__init__()

        if start_date is None:
            start_date = datetime.datetime(2021, 1, 1)
        self.date = start_date.strftime('%Y-%m-%d')
        self.date_index = pd.date_range(start=self.date, periods=96, freq='15min')
        self.time_of_day = time_of_day
        self.tick = 0
        self.tod_surplus = None  # Time of day when surplus electricity is available
        self.tod_deficit = None  # Time of day when electricity is needed from the grid
        self.agent_list = agents_list
        self.schedule = RandomActivation(self)
        self.all_assets = {}
        self.all_agents = self.create_agents()
        self.datacollector = DataCollector(model_reporters={
            "energy costs": get_energy_expenses,
            "avg agent demand": get_average_demand,
            "total agent demand": get_total_demand,
            "total generation": get_total_supply,
            "avg generation": get_average_supply})

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        self.datacollector.collect(self)
        self.date = self.tick_to_date(self.tick + 1)

    def create_agents(self):
        """Create agents and add them to the schedule."""
        all_agents = {}
        for agent_details in self.agent_list:
            if agent_details['agent_type'] is Coordinator:
                agent = Coordinator(unique_id=self.next_id(), model=self)
            elif agent_details['agent_type'] is Residential:
                agent = Residential(unique_id=self.next_id(),
                                    member_name=agent_details['member_name'],
                                    member_type=agent_details['member_type'],
                                    demand_flexibility=agent_details['demand_flexibility'],
                                    asset_list=agent_details['asset_list'],
                                    model=self)
            elif agent_details['agent_type'] is NonResidential:
                agent = NonResidential(unique_id=self.next_id(), member_name=agent_details['member_name'],
                                       member_type=agent_details['member_type'],
                                       demand_flexibility=agent_details['demand_flexibility'],
                                       asset_list=agent_details['asset_list'],
                                       model=self)
            elif agent_details['agent_type'] is EVChargingStation:
                agent = EVChargingStation(unique_id=self.next_id(), member_name=agent_details['member_name'],
                                          member_type=agent_details['member_type'],
                                          demand_flexibility=agent_details['demand_flexibility'],
                                          asset_list=agent_details['asset_list'], model=self)
            self.schedule.add(agent)
            if agent_details['agent_type'] in all_agents:
                all_agents[agent_details['agent_type']].append(agent)
            else:
                all_agents[agent_details['agent_type']] = [agent]

        return all_agents

    def run_simulation(self, steps=1, time_tracking=False, debug=False):
        """
        Runs the model for a specific amount of steps.
        :param steps: int: number of steps (in years)
        :param time_tracking: Boolean
        :param debug: Boolean
        :return:
            output: Dataframe: all information that the datacollector gathered
        """

        start_time = time.time()

        for tick in range(steps):
            if debug:
                print(f'Step: {tick}')
            # self.date = self.tick_to_date(tick + 1)
            self.step()

        if time_tracking:
            run_time = round(time.time() - start_time, 2)
            print(f'Run time: {run_time} seconds')

            print('Simulation completed!')

        results = self.datacollector.get_model_vars_dataframe()
        return results

    @staticmethod
    def tick_to_date(tick):
        """
        Converts a tick to a date
        :param tick: int: tick number
        :return:
            date: string: date in format "YYYY-MM-DD"
        """
        year = 2021
        days = tick
        date = datetime.datetime(year, 1, 1) + datetime.timedelta(days - 1)
        date = date.strftime('%Y-%m-%d')
        return date
