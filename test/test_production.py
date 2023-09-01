import pandas as pd
import sys
sys.path.append("/home/nick/Production-Control/src")
from production import rate


data = pd.read_csv("/home/nick/Production-Control/test/tasks.csv")

assembly = rate(data)

print(assembly.cycle_times)
print(f"Expected Hourly Rate: {assembly.simulation['Hourly Rate'].mean()}")
