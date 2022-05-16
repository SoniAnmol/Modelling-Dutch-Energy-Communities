"""
This module contains all agent classes.
"""

import datetime
import random

import numpy as np
import pandas as pd
from mesa import Agent

from model.enumerations import *

random.seed(123)

# Read the model input data
df = pd.read_csv("../data/processed/model_input_data.csv", parse_dates=['Local'], infer_datetime_format=True,
                 index_col=0)


class Coordinator(Agent):
    """This agent manages the energy community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.member_type = MemberType.COORDINATOR
        self.day_ahead_demand = self.get_day_ahead_demand()
        self.day_ahead_supply = self.get_day_ahead_supply()
        self.energy_deficit = 0
        self.energy_cost = 0
        start_date = datetime.datetime(2021, 1, 1)
        self.date = start_date
        self.tick = 0
        pass

    def step(self):
        self.date = self.tick_to_date(self.tick + 1)
        self.calculate_energy_deficit()
        self.energy_cost = self.get_energy_prices()
        self.release_tod_schedule()
        self.distribute_revenue()

    def balance_supply_demand(self):
        """This method balances the daily supply and demand for the energy community."""
        # TODO: Implement the supply/demand balance
        # Calculate amount of electricity to be imported from the grid
        pass

    def get_demand_schedule(self):
        """
        Returns the aggregated demand of all consumers.
        """
        agg_demand_schedule = np.zeros(96)
        for agent in self.model.schedule.agents:
            if agent.member_type is MemberType.CONSUMER or agent.member_type is MemberType.PROSUMER:
                agg_demand_schedule += agent.demand_schedule
        return agg_demand_schedule

    def get_supply_schedule(self):
        """
        Returns the aggregated supply from all generation assets.
        """
        agg_supply_schedule = np.zeros(96)
        for agent in self.model.schedule.agents:
            if agent.member_type is MemberType.ASSET:
                agg_supply_schedule += agent.supply_schedule
        return agg_supply_schedule

    def get_day_ahead_supply(self):
        """This method returns the day ahead supply of the energy community."""
        day_ahead_supply = np.zeros(96)
        for agent in self.model.schedule.agents:
            if agent.member_type is MemberType.ASSET:
                day_ahead_supply += agent.day_ahead_supply
        return day_ahead_supply

    def get_day_ahead_demand(self):
        day_ahead_demand = np.zeros(96)
        for agent in self.model.schedule.agents:
            if agent.member_type is MemberType.CONSUMER or agent.member_type is MemberType.PROSUMER:
                day_ahead_demand += agent.day_ahead_demand
        return day_ahead_demand

    def calculate_energy_deficit(self):
        self.day_ahead_demand = self.get_demand_schedule()
        self.day_ahead_supply = self.get_supply_schedule()
        self.energy_deficit = self.day_ahead_demand - self.day_ahead_supply

    def get_energy_prices(self):
        """Calculates the energy prices for the energy community."""
        unit_price = np.random.uniform(0.5, 1.5)
        energy_cost = unit_price * self.energy_deficit
        return energy_cost

    def release_tod_schedule(self):
        """This method releases the TOD schedule for the energy community."""
        day_ahead_deficit = self.day_ahead_demand - self.day_ahead_supply
        pass

    def distribute_revenue(self):
        """This method distributes the revenue to the consumers."""
        # TODO: Implement the revenue distribution
        pass

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


class Member(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model, member_name, member_type, asset_list):
        """ Initialize agent and variables.
        :param unique_id: int: unique identifier for the agent
        :param model: model: model in which the agent lives
        :param member_name: string: name of the member
        :param member_type: MemberType: type of the member (consumer, prosumer, asset)
        :param asset_list: list: list of assets the member owns. Leave empty if the member has no assets.
        """
        super().__init__(unique_id, model)
        self.member = member_name
        self.member_type = member_type
        start_date = datetime.datetime(2021, 1, 1)
        self.date = start_date.strftime('%Y-%m-%d')
        self.tick = 0
        self.load = 0
        self.tod_compliance = False
        self.demand_realized = None
        self.excess_generation = None
        self.assets = []
        item = None
        if self.member_type is MemberType.PROSUMER:
            for asset in asset_list:
                if asset['asset_type'] is Solar:
                    item = Solar(unique_id=self.model.next_id(), model=self.model,
                                 capacity=asset['capacity'], price=asset['price'], efficiency=asset['efficiency'],
                                 owner=self)
                elif asset['asset_type'] is Wind:
                    item = Wind(unique_id=self.model.next_id(), model=self.model)
                self.assets.append(item)
                self.model.schedule.add(item)
                if asset['asset_type'] in self.model.all_assets:
                    self.model.all_assets[asset['asset_type']].append(item)
                else:
                    self.model.all_assets[asset['asset_type']] = [item]
        else:
            self.assets = None

        self.demand_schedule = self.get_demand_schedule()
        self.generation_schedule = self.get_generation_schedule()
        self.adjust_schedules()
        self.day_ahead_demand, self.day_ahead_supply = self.generate_day_ahead_schedules()

    def step(self):
        self.date = self.tick_to_date(self.tick + 1)
        self.demand_schedule = self.get_demand_schedule()
        self.generation_schedule = self.get_generation_schedule()
        self.adjust_schedules()
        self.day_ahead_demand, self.day_ahead_supply = self.generate_day_ahead_schedules()
        pass

    def get_generation_schedule(self):
        """
        This method returns the aggregated generation schedule of all the assets owned by the Prosumer. Returns a series
        of zeros if the member is not a Prosumer.
        """
        index = pd.date_range(start=self.date, periods=96, freq='15min')
        generation_schedule = pd.Series(index=index, data=0)
        if self.member_type is MemberType.PROSUMER:
            for asset in self.assets:
                generation_schedule += asset.generate_supply_schedule()
        else:
            pass
        return generation_schedule

    def get_demand_schedule(self):
        """This method returns the demand schedule for the member_name."""
        demand_schedule = df.loc[self.date, self.member]
        return demand_schedule

    def generate_day_ahead_schedules(self):
        """Generates day ahead demand and (excess) generation for an agent."""
        tomorrow = (datetime.datetime.strptime(self.date, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        demand = df.loc[tomorrow, self.member]
        index = pd.date_range(start=tomorrow, periods=96, freq='15min')
        generation = pd.Series(index=index, data=0)
        if self.member_type is MemberType.PROSUMER:
            for asset in self.assets:
                generation += asset.day_ahead_supply_schedule()
        else:
            pass
        demand = (demand - generation).clip(lower=0)
        generation = (generation - demand).clip(lower=0)
        return demand, generation

    def adjust_schedules(self):
        """Modifies the demand schedule for an agent based on captive the TOD compliance."""
        realised_demand = None
        # Adjusting self consumption from the demand schedule and generation schedule
        if self.member_type is MemberType.PROSUMER:
            realised_demand = (self.demand_schedule - self.generation_schedule).clip(lower=0)
            # Updating the generation schedule based on captive consumption
            self.excess_generation = (self.generation_schedule - self.demand_schedule).clip(lower=0)

        if self.tod_compliance:
            pass
        # TODO: Implement the TOD compliance
        else:
            realised_demand = self.demand_schedule

        self.demand_realized = realised_demand

    def compute_energy_cost(self):
        """Computes the energy cost for a member"""
        pass

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


class Residential(Member):
    """A member_name of the residential community."""

    def __init__(self, unique_id, model, member_name, member_type, asset_list):
        super().__init__(unique_id, model, member_name, member_type, asset_list)
        pass

    def step(self):
        super(Residential, self).step()
        pass

    def get_demand_schedule(self):
        """This method returns the demand schedule for the member_name."""
        # Randomly pick a household type
        demand_schedule = df.loc[self.date, self.member]
        return demand_schedule


class NonResidential(Member):
    """A member_name of the residential community."""

    def __init__(self, unique_id, model, member_name, member_type, asset_list):
        super().__init__(unique_id, model, member_name, member_type, asset_list)
        pass

    def step(self):
        super(NonResidential, self).step()
        pass


class EVChargingStation(Member):
    """A member_name of the residential community."""

    def __init__(self, unique_id, model, member_name, member_type, asset_list):
        super().__init__(unique_id, model, member_name, member_type, asset_list)
        pass

    def step(self):
        super(EVChargingStation, self).step()
        pass


class Asset(Agent):
    """An asset of the energy community."""

    def __init__(self, unique_id, model, capacity=0, price=0, efficiency=0, owner=None):
        super().__init__(unique_id, model)
        start_date = datetime.datetime(2021, 1, 1)
        self.date = start_date.strftime('%Y-%m-%d')
        self.tick = 0
        self.member_type = MemberType.ASSET
        self.owner = owner
        self.price = price
        self.efficiency = efficiency
        self.capacity = capacity
        self.member_type = MemberType.ASSET
        self.asset_type = AssetType.SOLAR
        self.supply_schedule = self.generate_supply_schedule()
        self.day_ahead_schedule = self.day_ahead_supply_schedule()

        pass

    def step(self):
        self.date = self.tick_to_date(self.tick + 1)
        self.supply_schedule = self.generate_supply_schedule()
        self.day_ahead_schedule = self.day_ahead_supply_schedule()
        pass

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

    def generate_supply_schedule(self):
        pass

    def day_ahead_supply_schedule(self):
        pass


class Solar(Asset):
    """A solar asset of the energy community."""

    def __init__(self, unique_id, model, capacity=0, price=0, efficiency=0, owner=None):
        super().__init__(unique_id, model)
        self.owner = owner
        self.price = price
        self.efficiency = efficiency
        self.capacity = capacity
        self.member_type = MemberType.ASSET
        self.asset_type = AssetType.SOLAR
        self.supply_schedule = self.generate_supply_schedule()

    def generate_supply_schedule(self):
        """ Generates a schedule for the solar asset based on the capacity and efficiency of the solar panel"""
        super().generate_supply_schedule()
        supply_schedule = self.capacity * self.efficiency * df.loc[self.date, 'Direct [W/m^2]'] / 1000
        return supply_schedule

    def day_ahead_supply_schedule(self):
        """ Generates a schedule for the solar asset based on the capacity and efficiency of the solar panel"""
        super().day_ahead_supply_schedule()
        tomorrow = (datetime.datetime.strptime(self.date, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        supply_schedule = self.capacity * self.efficiency * df.loc[tomorrow, 'Direct [W/m^2]'] / 1000
        return supply_schedule

    def step(self):
        super(Solar, self).step()
        pass


class Wind(Asset):
    """A wind asset of the energy community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.member_type = MemberType.ASSET
        self.asset_type = AssetType.WIND
        self.supply_schedule = self.generate_supply_schedule()

    @staticmethod
    def generate_supply_schedule(mean=10, sigma=10):
        """Generates a mock supply schedule for an asset for a given day"""
        super().generate_supply_schedule()
        size = 96
        supply_schedule: np.ndarray | int | float | complex = np.random.normal(mean, sigma, size)
        return supply_schedule
