from model.model_code import EnergyCommunity
from model.agents import *
agent_counts = {
                Coordinator: 1,
                Residential: 300,
                Commercial: 20,
                Curio: 1,
                Sligro: 1,
                EVChargingStation: 3,
                Solar: 1,
                Wind: 1
            }

model = EnergyCommunity(agent_counts=agent_counts)
results = model.run_simulation(steps=365, time_tracking=True)
results.to_csv('../results/simulation_results.csv', index=False)
