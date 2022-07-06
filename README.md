[Home](https://sonianmol.com/)

# Exploring demand response in energy communities

This project is the masters thesis for M.Sc. Engineering and Policy Analysis at TU Delft. In this project, an
agent-based model of energy community is created using `mesa` library. This model serve as a testing ground for testing
demand response policies on the modeled energy communities.

## Authors

- [@SoniAnmol](https://www.github.com/SoniAnmol) - Anmol Soni

## Current state

This model under currently in development. This document will be updated shortly.

## General information

This project is a thesis project done in collaboration with [Croonwolter&Dros](https://croonwolterendros.nl/). This
model is primary focused on electric energy communities and can be extended to other energy sources. The model is used
to evaluate demand response with in energy communities while ensuring fair distribution of cost and benefits among
community members.

## Repository structure

```angular2html
./Modelling-Dutch-Energy-Communities/
│
├───data                         # contains the data for the model
│   ├───processed                # contains cleaned and processed data used by the model
│   └───raw                      # contains raw data acquired from the source
├───evidence_files               # contains verification and validation evidence files
│   ├───figures_validation       # contains the plots generated from validation tests
│   └───figures_verification     # contains the plots generated from verification tests
├───example                      # contains an example simulation run script and results
├───experiments                  # contains experiment setup and script for performing experiments with the model
│   └───figures                  # contains figures generated from experiment results
│       ├───groene_mient         # contains results generated from the results of experiments performed on Groene Mint
│       └───gridflex             # contains results generated from the results of experiments performed on GridFlex
├───images                       # contains figures and illustrations for the model
│   └───UML                      # contains UML diagrams of the model
├───model                        # contains the model and agent scripts
│   └───__pycache__
└───results                      # contains the script for extracting results from the model outputs

```


## Model

### System Relationship
Following system relationship is captured in the model.
<img src="images/Model-System-relationships.png">

### XLRM Framework
This model has adapted the following XLRM framework.
<img src="images/Model-XLRM.png" alt="xlrm_diagram">

## Community members
This model has following demand profiles in the data bank. These demand profiles can be combined in different
permutations and cobinations for creating community configurations.

- Three demand profiles for residential community members
- Four demand profiles for non-residential community members (office buildings)
- Demand profile of a School (MBO)
- Demand profile of an EV charging station with three slow chargers

