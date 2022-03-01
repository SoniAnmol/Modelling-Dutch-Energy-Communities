from model.model_code import EnergyCommunity
from model.agents import *
agent_counts = {
                Coordinator: 1,
                Residential: 10,
                Commercial: 1,
                Utility: 1,
                School: 1,
                EVChargingStation: 1,
                Solar: 1,
                Wind: 1
            }

model = EnergyCommunity(agent_counts=agent_counts)
results = model.run_simulation(steps=30)
print(results)
