"""
This module contains all agent classes.
"""

import datetime
import random
import math

import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'
from mesa import Agent

from model.enumerations import *

# random.seed(123)

# Read the model input data
df = pd.read_csv("data/processed/model_input_data.csv", parse_dates=['Local'], infer_datetime_format=True,
                 index_col=0)
electricity_costs = pd.read_csv("../data/processed/electricity_costs.csv", index_col=1)
electricity_costs = electricity_costs.to_dict(orient='index')


class Coordinator(Agent):
    """This agent manages the energy community."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.agent_type = AgentType.COORDINATOR
        self.total_energy_export = None
        self.total_energy_import = None
        self.date = self.model.date
        self.date_index = pd.date_range(start=self.date, periods=96, freq='15min')

    def step(self):
        self.update_date()
        self.date_index = pd.date_range(start=self.date, periods=96, freq='15min')
        self.balance_supply_and_demand()
        if self.model.participation_in_tod is not None and self.model.participation_in_tod > 0:
            self.release_tod_schedule()

    def balance_supply_and_demand(self):

        agg_supply = pd.Series(0, index=self.date_index)
        agg_demand = pd.Series(0, index=self.date_index)
        for agent in self.model.schedule.agents:
            if agent.agent_type is AgentType.CONSUMER or agent.agent_type is AgentType.PROSUMER:
                agg_demand += agent.realised_demand
            if agent.agent_type is AgentType.PROSUMER:
                agg_supply += agent.excess_generation
        energy_export = (agg_supply - agg_demand).clip(lower=0)
        energy_import = (agg_demand - agg_supply).clip(lower=0)
        total_energy_export = energy_export.sum()
        total_energy_import = energy_import.sum()

    def release_tod_schedule(self):
        tomorrow = (datetime.datetime.strptime(self.date, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        index = pd.date_range(start=tomorrow, periods=96, freq='15min')
        empty_series = pd.Series(0, index=index)
        day_ahead_demand = empty_series
        day_ahead_supply = empty_series
        # Get aggregated demand and supply for the next day
        agents = [AgentType.CONSUMER, AgentType.PROSUMER]
        for agent in self.model.schedule.agents:
            if agent.agent_type in agents:
                day_ahead_demand = day_ahead_demand + agent.day_ahead_demand
                day_ahead_supply = day_ahead_supply + agent.day_ahead_supply
        day_ahead_supply = self.adjust_generation_schedule(day_ahead_supply)
        index = pd.date_range(start=tomorrow, periods=96, freq='H')
        day_ahead_df = pd.DataFrame(index=index, data={'surplus': day_ahead_supply, 'deficit': day_ahead_demand})
        supply_threshold = day_ahead_df['surplus'].quantile(0.7)
        demand_threshold = day_ahead_df['deficit'].quantile(0.7)
        self.model.tod_surplus_timing = day_ahead_df[day_ahead_df['surplus'] > supply_threshold].index.to_list()
        self.model.tod_deficit_timing = day_ahead_df[day_ahead_df['deficit'] > demand_threshold].index.to_list()

    def adjust_generation_schedule(self, day_ahead_supply):
        if random.uniform(0, 1) < 5:
            day_ahead_supply = day_ahead_supply * (1 + random.uniform(0.5, self.model.uncertainties['X3']))
        else:
            day_ahead_supply = day_ahead_supply * (1 - random.uniform(0.5, self.model.uncertainties['X3']))
        return day_ahead_supply

    def update_date(self):
        self.date = self.model.date
        return None


class Member(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model, member_name, agent_type, member_type, demand_flexibility, asset_list):
        """ Initialize agent and variables.
        param unique_id: int: unique identifier for the agent
        :param model: model: model in which the agent lives
        :param member_name: string: name of the member
        :param member_type: MemberType: type of the member (consumer, prosumer, asset)
        :param asset_list: list: list of assets the member owns. Leave empty if the member has no assets.
        """
        super().__init__(unique_id, model)
        self.member_name = member_name
        self.agent_type = agent_type
        self.member_type = member_type
        self.date = self.model.date
        self.date_index = pd.date_range(start=self.date, periods=96, freq='15min')
        self.load = 0
        self.demand_flexibility = demand_flexibility
        self.realised_demand = pd.Series(0, index=self.date_index)
        self.excess_generation = pd.Series(0, index=self.date_index)
        self.assets = []
        self.shifted_load = 0  # Load shifted by the member as complaince of ToD schedule
        self.savings_ToD = 0  # Savings in Euros by complying with demand response
        # If agent is a prosumer, initialise assets
        if asset_list is not None:
            self.initialise_asset(asset_list)
        else:
            self.assets = None

        self.scheduled_demand = pd.Series(0, index=self.date_index)
        self.generation_schedule = pd.Series(0, index=self.date_index)
        self.day_ahead_demand = pd.Series(0, index=self.date_index)
        self.day_ahead_supply = pd.Series(0, index=self.date_index)
        self.energy_cost = None
        self.earnings = None
        self.average_lcoe = self.compute_average_lcoe()

    def step(self):
        super().step()
        self.update_date()
        self.get_demand_schedule()
        self.get_generation_schedule()
        self.generate_day_ahead_schedules()
        self.adjust_schedule_for_captive_consumption()
        self.adjust_schedule_for_tod()
        self.compute_energy_cost()
        self.compute_earnings()
        pass

    def initialise_asset(self, asset_list):
        item = None
        for asset in asset_list:
            if asset['asset_type'] is Solar:
                item = Solar(unique_id=self.model.next_id(), model=self.model,
                             capacity=asset['capacity'], capex=asset['price'], efficiency=asset['efficiency'],
                             owner=self)
            elif asset['asset_type'] is Wind:
                item = Wind(unique_id=self.model.next_id(), model=self.model)
            self.assets.append(item)
            self.model.schedule.add(item)
            if asset['asset_type'] in self.model.all_assets:
                self.model.all_assets[asset['asset_type']].append(item)
            else:
                self.model.all_assets[asset['asset_type']] = [item]

    def update_date(self):
        self.date = self.model.date
        return None

    def get_generation_schedule(self):
        """
        This method returns the aggregated generation schedule of all the assets owned by the Prosumer. Returns a series
        of zeros if the member is not a Prosumer.
        """
        index = pd.date_range(start=self.date, periods=96, freq='15min')
        generation_schedule = pd.Series(index=index, data=0)
        if self.agent_type is AgentType.PROSUMER:
            for asset in self.assets:
                generation_schedule += asset.generate_supply_schedule()
        else:
            pass
        self.generation_schedule = generation_schedule
        return None

    def get_demand_schedule(self):
        """This method returns the demand schedule for the member_name."""
        self.scheduled_demand = df.loc[self.date, self.member_name]
        return None

    def generate_day_ahead_schedules(self):
        """Generates day ahead demand and (excess) generation for an agent."""
        tomorrow = (datetime.datetime.strptime(self.date, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        demand = df.loc[tomorrow, self.member_name]
        index = pd.date_range(start=tomorrow, periods=96, freq='15min')
        generation = pd.Series(index=index, data=0)
        if self.agent_type is AgentType.PROSUMER:
            for asset in self.assets:
                generation += asset.day_ahead_supply_schedule()

        self.day_ahead_demand = (demand - generation).clip(lower=0)
        self.day_ahead_supply = (generation - demand).clip(lower=0)
        return None

    def adjust_schedule_for_captive_consumption(self):
        """Modifies the demand schedule for an agent based on captive generation"""
        # Adjusting self consumption from the demand schedule and generation schedule
        if self.agent_type is AgentType.PROSUMER:
            self.realised_demand = (self.scheduled_demand - self.generation_schedule).clip(lower=0)
            # Updating the generation schedule based on captive consumption
            self.excess_generation = (self.generation_schedule - self.scheduled_demand).clip(lower=0)
        else:
            self.realised_demand = self.scheduled_demand

    def adjust_schedule_for_tod(self):
        # Update the demand schedule based on demand response
        increased_consumption = 0
        reduced_consumption = 0
        if random.uniform(0, 1) <= self.model.participation_in_tod:
            if self.model.tod_surplus_timing is not None:
                if set(self.model.tod_surplus_timing) & set(self.realised_demand.index):
                    updated_schedule = self.realised_demand[self.model.tod_surplus_timing] * (
                            1 + self.demand_flexibility * random.uniform(self.model.demand_availability['minimum'],
                                                                         self.model.demand_availability['maximum']))
                    increased_consumption = updated_schedule.sum() - self.realised_demand[
                        self.model.tod_surplus_timing].sum()
                    increased_consumption = abs(increased_consumption)
                    self.realised_demand.loc[self.model.tod_surplus_timing] = updated_schedule
            if self.model.tod_deficit_timing is not None:
                if set(self.model.tod_deficit_timing) & set(self.realised_demand.index):
                    updated_schedule = self.realised_demand[self.model.tod_surplus_timing] * (
                            1 - self.demand_flexibility * random.uniform(self.model.demand_availability['minimum'],
                                                                         self.model.demand_availability['maximum']))
                    reduced_consumption = self.realised_demand[
                                              self.model.tod_surplus_timing].sum() - updated_schedule.sum()
                    reduced_consumption = abs(reduced_consumption)
                    self.realised_demand.loc[self.model.tod_surplus_timing] = updated_schedule
            self.shifted_load = max(increased_consumption, reduced_consumption)

    def compute_energy_cost(self):
        """Computes the energy cost for a member"""
        month = datetime.datetime.strptime(self.date, '%Y-%m-%d').strftime('%B')
        fixed_costs = electricity_costs[month]['Electricity Transport rate (Euro/day)'] + electricity_costs[month][
            'Fixed delivery rate (Euro/day)']
        variable_costs = electricity_costs[month]['Variable delivery rate (Euro/kWh)'] * self.realised_demand + \
                         electricity_costs[month][
                             'ODE tax (Environmental Taxes Act) (Euro/kWh)'] * self.realised_demand + \
                         electricity_costs[month]['Energy tax (Euro/kWh)'] * self.realised_demand + \
                         electricity_costs[month]['Variable delivery rate (Euro/kWh)'] * self.realised_demand
        variable_costs = variable_costs.sum()
        self.energy_cost = fixed_costs + variable_costs
        self.savings_ToD = electricity_costs[month]['Variable delivery rate (Euro/kWh)'] * self.shifted_load + \
                           electricity_costs[month][
                               'ODE tax (Environmental Taxes Act) (Euro/kWh)'] * self.shifted_load + \
                           electricity_costs[month]['Energy tax (Euro/kWh)'] * self.shifted_load + \
                           electricity_costs[month]['Variable delivery rate (Euro/kWh)'] * self.shifted_load
        self.energy_cost = self.energy_cost - self.savings_ToD

    def compute_average_lcoe(self):
        """Computes the average LCOE for a member"""
        if self.agent_type == AgentType.PROSUMER:
            lcoe = 0
            for asset in self.assets:
                lcoe += asset.lcoe
            average_lcoe = lcoe / len(self.assets)
        else:
            average_lcoe = 0
        return average_lcoe

    def compute_earnings(self):
        """Computes the earnings for a member"""
        self.earnings = 0
        if self.agent_type is AgentType.PROSUMER:
            self.earnings = self.excess_generation.sum() * self.average_lcoe
        else:
            pass


class Asset(Agent):
    """An asset of the energy community."""

    def __init__(self, unique_id, model, capacity, efficiency, owner, asset_age,
                 estimated_lifetime_generation, capex, opex, discount_rate=0.055):
        super().__init__(unique_id, model)
        self.date = self.model.date
        self.agent_type = AgentType.ASSET
        self.owner = owner
        self.efficiency = efficiency
        self.capacity = capacity
        self.asset_age = asset_age
        self.estimated_lifetime_generation = estimated_lifetime_generation
        if self.estimated_lifetime_generation == 0:
            self.estimate_lifetime_generation()
        self.supply_schedule = None
        self.day_ahead_schedule = None
        self.discount_rate = discount_rate
        self.capex, self.opex = self.compute_capex_and_opex(capex, opex)
        self.lcoe = None
        self.compute_lcoe()

    def step(self):
        super().step()
        self.date = self.model.date
        self.supply_schedule = self.generate_supply_schedule()
        self.day_ahead_schedule = self.day_ahead_supply_schedule()
        pass

    def generate_supply_schedule(self):
        pass

    def day_ahead_supply_schedule(self):
        pass

    def estimate_lifetime_generation(self):
        """Estimates lifetime generation/supply of the asset"""
        lifespan = 25 - self.asset_age
        hours_per_year = 365 * 24
        if self.asset_type is AssetType.SOLAR:
            capacity_factor = 9.138 / 100
        elif self.asset_type is AssetType.WIND:
            capacity_factor = 27.89 / 100
        # TODO: Add capacity factor for battery
        annual_generation_kWh = hours_per_year * capacity_factor / 1000
        self.estimated_lifetime_generation = lifespan * annual_generation_kWh * self.capacity

    def compute_lcoe(self):
        """Calculates LCOE of the solar plant"""
        lifespan = 25 - self.asset_age
        expenses = (self.capex + self.opex) / ((1 - self.discount_rate) ** (lifespan + 1))
        electricity_supplied = self.estimated_lifetime_generation / ((1 - self.discount_rate) ** (lifespan + 1))
        self.lcoe = expenses / electricity_supplied

    def compute_capex_and_opex(self, capex, opex):
        if self.asset_type is AssetType.SOLAR:
            if capex == 0:
                capex = 1.39 * self.capacity
            if opex == 0:
                opex = capex * 0.1
        elif self.asset_type is AssetType.WIND:
            if capex == 0:
                capex = 2460000 * self.number_of_turbines
            if opex == 0:
                opex = capex * 0.1
        return capex, opex


class Solar(Asset):
    """A solar asset of the energy community."""

    def __init__(self, unique_id, model, capacity=0, efficiency=0, owner=None, asset_age=0,
                 estimated_lifetime_generation=0, capex=0, opex=0, discount_rate=0.055):
        self.asset_type = AssetType.SOLAR
        super(Solar, self).__init__(unique_id, model, capacity, efficiency, owner, asset_age,
                                    estimated_lifetime_generation, capex, opex, discount_rate)

    def generate_supply_schedule(self):
        """ Generates a schedule for the solar asset based on the capacity and efficiency of the solar panel"""
        super().generate_supply_schedule()
        supply_schedule = self.capacity * self.efficiency * df.loc[self.date, 'Direct [W/m^2]'] / 1000000
        return supply_schedule

    def day_ahead_supply_schedule(self):
        """ Generates a schedule for the solar asset based on the capacity and efficiency of the solar panel"""
        super().day_ahead_supply_schedule()
        tomorrow = (datetime.datetime.strptime(self.date, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        supply_schedule = self.capacity * self.efficiency * df.loc[tomorrow, 'Direct [W/m^2]'] / 1000000
        return supply_schedule


class Wind(Asset):
    """A wind asset of the energy community."""

    def __init__(self, unique_id, model, capacity=0, efficiency=0, owner=None, asset_age=1,
                 estimated_lifetime_generation=0, capex=0, opex=0, discount_rate=0.055, number_of_turbines=1,
                 rotor_diameter=125, avg_air_density=1.23):
        self.asset_type = AssetType.WIND
        self.number_of_turbines = number_of_turbines
        self.rotor_diameter = rotor_diameter
        self.avg_air_density = avg_air_density
        self.efficiency = 59.3 / 100  # Betz limit
        self.swept_area = math.pi * (self.rotor_diameter / 2) ** 2
        super(Wind, self).__init__(unique_id, model, capacity, efficiency, owner, asset_age,
                                   estimated_lifetime_generation, capex, opex, discount_rate)

    def generate_supply_schedule(self):
        """ Generates a schedule for the wind asset based on the capacity and efficiency of the wind turbine"""
        super().generate_supply_schedule()
        wind_speed = df.loc[self.date, 'Direct [W/m^2]']
        wind_speed[wind_speed > 30] = 0  # Wind turbine shuts down if wind speed is greater than 30 m/s
        supply_schedule = 0.5 * self.avg_air_density * self.swept_area * np.power(wind_speed,
                                                                                  3) * self.efficiency * self.number_of_turbines
        return supply_schedule

    def day_ahead_supply_schedule(self):
        """ Generates a schedule for the wind asset based on the capacity and efficiency of the wind turbine"""
        super().day_ahead_supply_schedule()
        tomorrow = (datetime.datetime.strptime(self.date, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        wind_speed = df.loc[tomorrow, 'Direct [W/m^2]']
        wind_speed[wind_speed > 30] = 0
        supply_schedule = 0.5 * self.avg_air_density * self.swept_area * np.power(wind_speed,
                                                                                  3) * self.efficiency * self.number_of_turbines
        return supply_schedule


class Battery(Asset):
    def __init__(self, unique_id, model, capacity=0, efficiency=0, owner=None, asset_age=1,
                 estimated_lifetime_generation=0, capex=0, opex=0, discount_rate=0.055):
        self.asset_type = AssetType.BATTERY_STORAGE
        super(Battery, self).__init__(unique_id, model, capacity, efficiency, owner, asset_age,
                                      estimated_lifetime_generation, capex, opex, discount_rate)
