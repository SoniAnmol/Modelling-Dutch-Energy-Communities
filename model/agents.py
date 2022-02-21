"""
This module contains all agent classes.
"""

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
        pass

    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        pass


class Residential(Member):
    """A member of the residential community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        pass

    def step(self):
        print("Hi, I am residential agent " + str(self.unique_id) + ".")
