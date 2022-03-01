[Home](https://sonianmol.com/) | [About](https://sonianmol.com/about)
| [My projects](https://sonianmol.com/my_projects/)

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

A thesis committee has been set up to evaluate the model and end results.

<img src="https://drive.google.com/uc?export=view&id=1vacWxsx2M5plE96QXIcEscDwYRqNsp0t" alt="Thesis Committee" style="width: 80%; margin: 0.5cm">

## Current state

This model is currently in development. This is the initial commit of the model.

## Introduction

TODO

## Model

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

**`Member`**:
This agent represents a member of the community. Number of members remains constant during the model run. A `Member` can
make following actions:

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

# Data

TODO

# Results

TODO

# Conclusion

TODO
