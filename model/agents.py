"""
This module contains all agent classes.
"""

import numpy as np
from mesa import Agent

from model.enumerations import *


class Coordinator(Agent):
    """This agent manages the energy community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.member_type = MemberType.COORDINATOR
        self.day_ahead_demand = 0
        self.day_ahead_supply = 0
        self.energy_deficit = 0
        self.energy_cost = 0
        pass

    def step(self):
        self.calculate_energy_deficit()
        self.energy_cost = self.get_energy_prices()
        self.release_tod_schedule()
        self.distribute_revenue()

    def balance_supply_demand(self):
        """This method balances the daily supply and demand for the energy community."""
        # TODO: Implement the supply/demand balance
        pass

    def get_demand_schedule(self):
        """
        Returns the aggregated demand of all consumers.
        """
        agg_demand_schedule = 0
        for agent in self.model.schedule.agents:
            if agent.member_type is MemberType.CONSUMER or agent.member_type is MemberType.PROSUMER:
                agg_demand_schedule += agent.demand_schedule
        return agg_demand_schedule

    def get_supply_schedule(self):
        """
        Returns the aggregated supply from all generation assets.
        """
        agg_supply_schedule = 0
        for agent in self.model.schedule.agents:
            if agent.member_type is MemberType.ASSET:
                agg_supply_schedule += agent.supply_schedule
        return agg_supply_schedule

    def calculate_energy_deficit(self):
        self.day_ahead_demand = self.get_demand_schedule()
        self.day_ahead_supply = self.get_supply_schedule()
        self.energy_deficit = self.day_ahead_demand - self.day_ahead_supply

    def get_energy_prices(self):
        """Calculates the energy prices for the energy community."""
        unit_price = np.random.uniform(0.5, 1.5)
        energy_cost = unit_price * self.energy_deficit
        return energy_cost

    def set_up_energy_community(self):
        """
        :return:
        """
        self.assess_community_requirement()
        self.set_up_assets()
        # TODO: Implement the energy community setup
        pass

    def assess_community_requirement(self):
        """This method assesses the community's energy requirement and recommends the appropriate assets.
        The recommendation could be either a generation or storage asset."""
        historical_demand_data = self.get_historical_demand_data()
        historical_supply_data = self.get_historical_supply_data()
        energy_difference = historical_demand_data - historical_supply_data
        if energy_difference > 0:
            self.set_up_storage()
        elif energy_difference < 0:
            self.set_up_generation()
        return None

    def set_up_storage(self):
        """This method sets up the storage assets for the energy community."""
        # TODO: Implement the storage setup
        pass

    def set_up_generation(self):
        """This method sets up the generation assets for the energy community."""
        # TODO: Implement the generation setup
        pass

    @staticmethod
    def get_historical_demand_data():
        """This method returns the historical demand data for the energy community."""
        # TODO: Implement the historical demand data retrieval
        pass
        return None

    @staticmethod
    def get_historical_supply_data():
        """This method returns the historical supply data for the energy community."""
        # TODO: Implement the historical supply data retrieval
        pass
        return None

    def set_up_assets(self):
        """This method sets up the assets for the energy community."""
        # TODO: Implement the asset setup
        pass

    def release_tod_schedule(self):
        """This method releases the TOD schedule for the energy community."""
        # TODO: Implement the TOD schedule release
        pass

    def distribute_revenue(self):
        """This method distributes the revenue to the consumers."""
        # TODO: Implement the revenue distribution
        pass


class Member(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.load = 0
        self.tod_compliance = False
        self.demand_schedule = self.get_demand_schedule()
        self.demand_realized = self.modify_demand_schedule()
        self.day_ahead_demand = self.generate_day_ahead_demand()
        self.member_type = MemberType.CONSUMER
        pass

    def step(self):
        self.demand_schedule = self.get_demand_schedule()
        self.demand_realized = self.modify_demand_schedule()
        self.day_ahead_demand = self.generate_day_ahead_demand()
        pass

    def get_demand_schedule(self):
        """This method returns the demand schedule for the member."""
        demand_schedule = self.generate_day_ahead_demand()
        return demand_schedule

    @staticmethod
    def generate_day_ahead_demand(mean=50, sigma=10):
        """Generates mock day ahead demand for an agent for a given day"""
        size = 24
        demand: np.ndarray | int | float | complex = np.random.normal(mean, sigma, size)
        return demand

    def modify_demand_schedule(self):
        """Modifies the demand schedule for an agent based on the TOD compliance."""
        if self.tod_compliance:
            pass
        # TODO: Implement the TOD compliance
        else:
            realised_demand = self.demand_schedule
        return realised_demand


class Residential(Member):
    """A member of the residential community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        pass

    def step(self):
        super(Residential, self).step()
        pass


class Commercial(Member):
    """A member of the residential community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        pass

    def step(self):
        super(Commercial, self).step()
        pass


class Utility(Member):
    """A member of the residential community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        pass

    def step(self):
        super(Utility, self).step()
        pass


class EVChargingStation(Member):
    """A member of the residential community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        pass

    def step(self):
        super(EVChargingStation, self).step()
        pass


class School(Member):
    """A member of the residential community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        pass

    def step(self):
        super(School, self).step()
        pass


class Asset(Agent):
    """An asset of the energy community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.owner = {}
        self.supply_schedule = self.generate_supply_schedule()
        self.supply_realized = self.modify_supply_schedule()
        self.member_type = MemberType.ASSET
        pass

    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        self.supply_schedule = self.generate_supply_schedule()
        # print(
        #     "Hi, I am" + str(self.member_type) + "asset ." + "My unique ID is " + str(self.unique_id) + ".")
        pass

    @staticmethod
    def generate_supply_schedule(mean=10, sigma=10):
        """Generates a mock supply schedule for an asset for a given day"""
        size = 24
        supply_schedule: np.ndarray | int | float | complex = np.random.normal(mean, sigma, size)
        return supply_schedule

    def modify_supply_schedule(self):
        """Modifies the supply schedule for an asset based on the TOD compliance."""
        # TODO: Implement the weather dependence
        return self.supply_schedule

class Solar(Asset):
    """A solar asset of the energy community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.member_type = MemberType.ASSET
        self.asset_type = AssetType.SOLAR
        pass


class Wind(Asset):
    """A wind asset of the energy community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.member_type = MemberType.ASSET
        self.asset_type = AssetType.WIND
        pass
