"""
This module contains all agent classes.
"""

import numpy as np

from mesa import Agent


class Coordinator(Agent):
    """This agent manages the energy community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        pass

    def step(self):
        print("Hi, I the coordinator agent " + str(self.unique_id) + ".")


class Member(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.load = 0
        self.demand = 0
        pass

    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        pass

    @staticmethod
    def generate_demand(mean=50, sigma=10):
        """Generates a mock demand for agent for a given day"""
        size = 24
        demand: np.ndarray | int | float | complex = np.random.normal(mean, sigma, size)
        return demand


class Residential(Member):
    """A member of the residential community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        pass

    def step(self):
        self.demand = self.generate_demand()
        print("Hi, I am residential agent " + str(self.unique_id) + "." + "My load is " + str(self.demand) + ".")
