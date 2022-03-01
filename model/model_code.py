import time

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

from model.agents import *


class EnergyCommunity(Model):
    """A model with some number of agents."""

    def __init__(self, agent_counts=None):
        super().__init__()
        if agent_counts is None:
            self.agent_counts = {
                Coordinator: 1,
                Residential: 10,
                Commercial: 1,
                Utility: 1,
                School: 1,
                EVChargingStation: 1,
                Solar: 1,
                Wind: 1
            }
        else:
            self.agent_counts = agent_counts
        self.schedule = RandomActivation(self)
        self.all_agents = self.create_agents()
        self.datacollector = DataCollector(model_reporters={
            "energy costs": self.get_energy_expenses})

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
                elif agent_type is Utility:
                    agent = Utility(self.next_id(), self)
                elif agent_type is School:
                    agent = School(self.next_id(), self)
                elif agent_type is EVChargingStation:
                    agent = EVChargingStation(self.next_id(), self)
                elif agent_type is Solar:
                    agent = Solar(self.next_id(), self)
                elif agent_type is Wind:
                    agent = Wind(self.next_id(), self)
                self.schedule.add(agent)
                if agent_type in all_agents:
                    all_agents[agent_type].append(agent)
                else:
                    all_agents[agent_type] = [agent]
        return all_agents

    def get_energy_expenses(self):
        """Returns the current energy prices."""
        return self.all_agents[Coordinator][0].energy_cost

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

        for _ in range(steps):
            if debug:
                print(f'Step: {_}')
            self.step()

        if time_tracking:
            run_time = round(time.time() - start_time, 2)
            print(f'Run time: {run_time} seconds')

            print('Simulation completed!')

        results = self.datacollector.get_model_vars_dataframe()
        return results
