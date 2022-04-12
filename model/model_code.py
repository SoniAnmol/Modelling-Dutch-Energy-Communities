# import datetime
import time

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

from model.data_reporters import *


class EnergyCommunity(Model):
    """A model with some number of agents."""

    date = None

    def __init__(self, agent_counts=None):
        super().__init__()
        # start_date = datetime.datetime(2021, 1, 1)
        # self.date = start_date.strftime('%Y-%m-%d')
        # self.date = start_date
        if agent_counts is None:
            self.agent_counts = {
                Coordinator: 1,
                Residential: 150,
                Commercial: 1,
                Curio: 1,
                Sligro: 1,
                KoningDrinks: 1,
                EVChargingStation: 1,
                Solar: 1,
                Wind: 0
            }
        else:
            self.agent_counts = agent_counts
        self.schedule = RandomActivation(self)
        self.all_agents = self.create_agents()
        self.datacollector = DataCollector(model_reporters={
            "energy costs": get_energy_expenses,
            "avg agent demand": get_average_demand,
            "total agent demand": get_total_demand,
            "total generation": get_total_supply,
            "avg generation": get_average_supply})
        # self.date = tick_to_date(self.tick)

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        self.datacollector.collect(self)

    def create_agents(self):
        """Create agents and add them to the schedule."""
        agent = 0
        all_agents = {}
        for agent_type, agent_count in self.agent_counts.items():
            for _ in range(agent_count):
                if agent_type is Coordinator:
                    agent = Coordinator(0, self)
                elif agent_type is Residential:
                    agent = Residential(self.next_id(), self)
                elif agent_type is Commercial:
                    agent = Commercial(self.next_id(), self)
                elif agent_type is Curio:
                    agent = Curio(self.next_id(), self)
                elif agent_type is Sligro:
                    agent = Sligro(self.next_id(), self)
                elif agent_type is KoningDrinks:
                    agent = KoningDrinks(self.next_id(), self)
                elif agent_type is EVChargingStation:
                    agent = EVChargingStation(self.next_id(), self)
                elif agent_type is Solar:
                    agent = Solar(self.next_id(), self, capacity=960, efficiency=0.20, price=0.15,
                                  owner=KoningDrinks)
                elif agent_type is Wind:
                    agent = Wind(self.next_id(), self)
                self.schedule.add(agent)
                if agent_type in all_agents:
                    all_agents[agent_type].append(agent)
                else:
                    all_agents[agent_type] = [agent]
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

    # @staticmethod
    # def tick_to_date(tick):
    #     """
    #     Converts a tick to a date
    #     :param tick: int: tick number
    #     :return:
    #         date: string: date in format "YYYY-MM-DD"
    #     """
    #     year = 2021
    #     days = tick
    #     date = datetime.datetime(year, 1, 1) + datetime.timedelta(days - 1)
    #     date = date.strftime('%Y-%m-%d')
    #     return date
