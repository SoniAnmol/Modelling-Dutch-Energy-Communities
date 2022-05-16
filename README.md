[Home](https://sonianmol.com/)

# Modelling Dutch Energy Communities

This is an agent-based simulation model of a Dutch energy community.
<br>
<img src="https://www.ped-interact.eu/wp-content/uploads/2021/05/Energy-Community.png" alt="Illustration of a energy community" style=" width: 80%; margin: 0.5cm">
<br>
<small>Image
source: [Energy Community](https://www.ped-interact.eu/wp-content/uploads/2021/05/Energy-Community.png)</small>
<br>

## Table of contents:

- [General information](#general-information)
- [Current state](#current-state)
- [Introduction](#introduction)
- [Model](#model)
- [Data](#data)
- [Results](#results)
- [Conclusion](#conclusion)

## General information

This project is a thesis project done in collaboration with [Croonwolter&Dros](https://croonwolterendros.nl/). This
model is primary focused on electric energy communities and can be extended to other energy sources. The model is used
to evaluate demand response with in energy communities while ensuring fair distribution of cost and benefits among
community members.

## Current state

This model is currently in development. This is the initial commit of the model.

## Introduction

TODO

## Model

This project takes a case study approach for the model.
The municipality of Breda, the province of North Brabant and Enexis (DSO)
share a vision for the future energy systems (electricity, heat, storage and conversion) for the region.
They want to consider Hazeldonk, a small business area in Breda as a pilot project.
In addition to this, an EV-bus depot is planned in the area which will be used for the docking and charging of 
electric buses.
Thus, the municipality of Breda is looking for a community energy project in Hazeldonk with active participation
from actors for the development of their energy system in this area aligned with that of others.

The composition of energy community is as follows:
1. Residential houses: 150 starter apartments in two buildings (75 each).
2. Schools: 2 School buildings.
3. Office buildings:
4. Municipality Bus-EV charging stations/terminal: 1 charging station.

Following is the power interest matrix of the stakeholders involved in the project:
<br>
<img src="images/Thesis%20-%20Stakeholder%20matrix.jpg" alt="power-interest-matrix" style=" width: 80%; margin: 0.5cm">
<br>

The stakeholders shown above are arranged based on their interest and power to influence the decision regarding
community energy projects. The grid shown above represents the decision arena for the project.
The four grids in the decision arena are:

**Defenders**:
The defenders are the actors with highest power in the decision arena but also with the lowest interest in the project.
The province of North Brabant is the most powerful actor as it possesses the governing power.
However, this project is not the highest priority for the province, and they have a relatively neutral interest level.

**Promoters**:
Promoters are the project propagators with the highest interest and power in the decision arena.
The municipality of Breda is the second most powerful actor and has high interest in the project as they have issued
the expression of interest. Enexis, the DSO of the area has decision-making power as they own the distribution assets,
and they also have relatively high interest in the project.

**Latents**:
Latents are the actors with low decision-making power and high interest levels. Both housing cooperation and School
(Curio) are interested in the project for reducing the energy costs and contributing sustainability of the
neighbourhood.

**Apathetic**: 
Apathetic are the actors with low decision-making power and low interest levels. Residents of the rented apartments,
existing businesses and scouting are relatively less interested in the project and have low decision-making power as
they are not involved in the project yet.

### Conceptualisation

This is the initial conceptualisation of the model. This project is still in development and the conceptualisation is
not yet complete/finalised.

#### Model conceptualisation

This model is based on a proposed energy community in Hazeldonk, Breda. In this model, community members are agents and
the energy community is the environment. Time step of the model is 1 day and the model runs for 30 steps (period of 1
month).

#### Agents conceptualisation

`Coordinator`:
This agent is responsible for following tasks in the energy community.
1. assessing the current state of the energy community and making investment decisions
2. balance_supply_demand
3. release_tod_schedule
4. distribute_costs_and_benefits

Assessment of community requirement:
The model is run for 30 steps (period of 1 month) with existing assets of energy community.
Based on the results of previous runs, Coordinator will assess the average energy deficit or surplus.
If energy is deficit, Coordinator will set up a generation asset.
If energy is surplus, Coordinator will set up a storage asset.

`set_up_generation_asset`:
If energy is deficit, Coordinator will set up a generation asset.
Coordinator will determine the size of the asset based on the energy deficit using following formula:

(Daily kWh ÷ average sun hours) x efficiency_factor = solar system size
The efficiency factor is based on the average efficiency of the solar system.

kWh = 0.01328 x (rotor diameter (feet)))^2 x (average wind speed (mph))^3

Source: NREL

`set_up_storage_asset`:
If energy is surplus, Coordinator will set up a storage asset. Coordinator will determine the size of the asset based on
the energy surplus using following formula:

battery size = Daily kWh x (1 + DoD)
DoD: Depth of Discharge (percentage)

All the batteries in the model have respective depletion factors after each charge discharge cycle. After complete
depletion, the battery will be replaced and additional cost will be added for the community. Battery in the model is
designed for one day back-up. This will result in smaller battery size which can be easily replaced after depletion.

Assumptions:
1. efficiency_factor considered for system size is assumed to be constant across brands and systems.
2. Average solar peak hours and average wind speed is also assumed to be constant for simplicity.

##### Fair investment opportunities for the energy community members

After finalising the asset type and size, Coordinator will ask interested members to invest in the asset. Not all the
interested members will be able to invest in the asset and some of them will be left out. This will be done by
introducing a random opportunity of investment factor. The filtered interested members will be asked to invest in the
asset. The investment by each member is capped so that commercial parties do not buy the major equity share of the
asset.

Assumptions: 
~~1. Non-residential energy community members are always interested in investing the asset.~~
~~2. Residential member's investment capacity is limited and function of annual household income.~~
~~3. Higher equity share in the community asset will result in higher influence in decision-making.~~

**`Member`**:
This agent represents a member of the community. A `Member` can make following actions:

- `invest`: invest in the community asset (e.g. solar panels, storage, etc.) at the start of simulation
- `comply_tod`: Comply with the time of day schedule released by community coordinator.

`Member` can be of following types:

1. `Residential`: A member of the community that is a resident (household).
2. `Commercial`: A member of the community that is a commercial building (office/SME).
3. `Utility`: A member of the community that is a utility (Streetlights, elevator, etc.).
4. `School`: A member of the community that is a school.
5. `EVChargingStation`: A member of the community that is a charging station for electric vehicles.

All `Member` have the following attributes:

- **Demand**: A community `Member` has three demand attributes:
   1. day_ahead_demand: The demand profile of the member for the next day.
   2. demand_schedule: The demand profile of the member for current day.
   3. demand_realised: The actualised demand profile of the member for current day.

Assumptions:
1. Number of members remains constant during the model run. 
2. It is assumed that the Prosumers first use captive generation for self consumption and share excess energy only.

# Data

This model uses following data:

1. Weather data: Weather data provided by Royal Netherlands Meteorological Institute [KNMI](https://www.knmi.nl/home) is
   used to get the hourly weather data for the simulation. This data is used to get the solar irradiance, wind speed,
   and temperature for simulating the generation form Solar PV and wind turbines. Data for the year 2021 is used for
   this model.
2. Electricity consumption data for non-residential buildings: Electricity consumption data for non-residential
   buildings is provided by the Croonwolter&dros (https://www.croonwolterendros.nl/en/). This data is collected for four
   office buildings and a school in the Netherlands. This data is used to infer the electricity consumption of offices
   and schools in the modelled community energy project.
3. Electricity consumption data for residential buildings: 
4. 

### Data Cleaning
The data collected from the respective sources is cleaned and checked for completeness. After cleaning, data is assessed
for semantic and syntactic correctness. Missing data is substituted with the nearest available data for minor data lapses.
Whereas, for major data lapses, average consumption data of the month for weekday or weekend is used respectively.

### Data preparation
After cleaning, data is prepared for modelling.

TODO

# Results

TODO

# Conclusion

TODO
