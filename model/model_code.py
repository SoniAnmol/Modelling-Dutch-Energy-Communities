# import datetime
import time

from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector

from model.data_reporters import *


class EnergyCommunity(Model):
    """A model with some number of agents."""

    date = None

    def __init__(self,
                 levers=None,
                 uncertainties=None,
                 agents_list=None,
                 start_date=None, ):
        super().__init__()

        if levers is None:
            self.levers = {
                "L1": 0.5,
                # Percentage of members participating in the demand response program (Social)
                "L2": 0.2,
                # Percentage of flexible (shift-able)  demand for residential community members (Technical)
                "L3": 0.3,
                # Percentage of flexible (shift-able)  demand for non-residential community members (Technical)
            }
        else:
            self.levers = levers

        if uncertainties is None:
            self.uncertainties = {
                "X1": 0.30,
                # Minimum percentage of flexible demand available for demand response on a single day (Social)
                "X2": 0.75,
                # Maximum percentage of flexible demand available for demand response on a single day (Social)
                "X3": 0.80,
                # Percentage accuracy of day-ahead generation projections from renewable assets (Technical)
            }
        else:
            self.uncertainties = uncertainties

        if start_date is None:
            start_date = datetime.datetime(2021, 1, 1)
        self.date = start_date.strftime('%Y-%m-%d')
        self.date_index = pd.date_range(start=self.date, periods=96, freq='15min')

        self.demand_availability = {'minimum': self.uncertainties['X1'],
                                    'maximum': self.uncertainties['X2']}
        self.participation_in_tod = self.levers['L1']
        self.tick = 0
        self.tod_surplus_timing = None  # Time of day when surplus electricity is available
        self.tod_deficit_timing = None  # Time of day when electricity is needed from the grid
        self.agent_list = agents_list
        self.schedule = BaseScheduler(self)
        self.all_assets = {}
        self.create_agents()
        self.datacollector = DataCollector(model_reporters={
            "date": get_date,
            # date or the time step for the model simulation
            "M1: realised_demand": get_realised_demand,
            # realised demand after incorporating demand response
            "M2: scheduled_demand": get_scheduled_demand,
            # demand before incorporating demand response
            "M3: shifted_load": get_shifted_load,
            # amount of load moved/shifted because of demand response
            "M4: total_generation": get_generation,
            # generation from the renewable assets in the simulation model
            "M5: savings_on_ToD": get_savings,
            # savings made by avoiding import of electricity from grid by community members
            "M6: energy_costs": get_energy_cost
            # total expenses made by community members for procuring electricity from the grid
        })

    def step(self):
        """Advance the model by one step."""
        super().step()
        self.schedule.step()
        self.datacollector.collect(self)
        self.tick += 1
        self.date = self.tick_to_date(self.tick)

    def create_agents(self):
        """Create agents and add them to the schedule."""
        for agent_details in self.agent_list:
            if agent_details['member_type'] is MemberType.COORDINATOR:
                agent = Coordinator(unique_id=self.next_id(), model=self)
            else:
                agent = Member(unique_id=self.next_id(),
                               member_name=agent_details['member_name'],
                               agent_type=agent_details['agent_type'],
                               member_type=agent_details['member_type'],
                               demand_flexibility=self.select_demand_flexibility(
                                   member_type=agent_details['member_type']),
                               asset_list=agent_details['asset_list'],
                               model=self)
            self.schedule.add(agent)
        return None

    def select_demand_flexibility(self, member_type):
        "Selects demand flexibility from levers for an agent based on member type"
        demand_flexibility = 0.20  # Default member flexibility
        if member_type is MemberType.RESIDENTIAL:
            demand_flexibility = self.levers['L2']
        elif member_type is MemberType.NON_RESIDENTIAL:
            demand_flexibility = self.levers['L3']
        return demand_flexibility

    def run_simulation(self, steps=365, time_tracking=False, debug=False):
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
