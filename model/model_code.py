import numpy as np
from mesa import Model
from mesa.time import RandomActivation

from model.agents import *


class EnergyCommunity(Model):
    """A model with some number of agents."""

    def __init__(self, number_of_agents):
        super().__init__()
        self.num_agents = number_of_agents
        self.schedule = RandomActivation(self)
        # Create community coordinator
        agent = Coordinator(0, self)
        self.schedule.add(agent)
        # Create agents
        for i in np.arange(1, self.num_agents + 1):
            agent = Residential(i, self)
            self.schedule.add(agent)

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
