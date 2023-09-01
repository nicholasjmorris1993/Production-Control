import re
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.offline import plot


def rate(df):
    assembly = Rate()
    assembly.assign_tasks(df)
    assembly.production_rate()
    assembly.plots()

    return assembly

class Rate:
    def assign_tasks(self, df):
        self.workers = int(df.loc[df["Item"] == "Workers", "Value"].values[0])
        self.tasks = df.copy().loc[df["Item"] != "Workers"].reset_index(drop=True)

        # calculate the expected amount of time each worker will spend doing their tasks
        total_time = self.tasks["Value"].sum()
        worker_time = total_time / self.workers

        # initialize the assignment dictionary
        assignment = dict()
        for i in range(self.workers):
            assignment[i] = list()

        # assign tasks to workers
        worker = 0
        time = 0
        for i in range(self.tasks.shape[0]):
            task_time = self.tasks["Value"][i]
            time += task_time

            if time <= worker_time * 1.1 or worker == self.workers - 1:
                assignment[worker].append(i)
            else:
                time = task_time
                worker += 1
                assignment[worker].append(i)

        # calculate the cycle time for each worker
        self.cycle_times = pd.DataFrame()
        for k in assignment.keys():
            tasks = assignment[k]
            cycle_time = self.tasks.iloc[tasks, 1].sum()
            cycle_times = pd.DataFrame({
                "Worker": [k + 1],
                "Cycle Time": [cycle_time],
                "Tasks": [" ".join(str(i + 1) for i in tasks)],
            })
            self.cycle_times = pd.concat([
                self.cycle_times, 
                cycle_times,
            ], axis="index").reset_index(drop=True)

    def production_rate(self):
        # simulate the tasks of each worker
        np.random.seed(0)
        self.simulation = pd.DataFrame()
        for i in range(self.cycle_times.shape[0]):
            self.simulation[f"Worker {i + 1}"] = np.random.exponential(
                scale=self.cycle_times["Cycle Time"][i],
                size=1000,
            )
        
        # calculate the cycle time across all workers
        self.simulation["Cycle Time"] = self.simulation.sum(axis=1)

        # calculate the hourly throughput
        self.simulation["Hourly Rate"] = 3600 / self.simulation["Cycle Time"]

    def plots(self):
        # plot the cycle times and throughput
        self.histogram(
            self.simulation, 
            x="Cycle Time", 
            bins=20, 
            title="Histogram On Cycle Time", 
            font_size=16,
        )
        self.histogram(
            self.simulation, 
            x="Hourly Rate", 
            bins=20, 
            title="Histogram On Hourly Rate", 
            font_size=16,
        )

    def histogram(self, df, x, bins=20, vlines=None, title="Histogram", font_size=None):
        bin_size = (df[x].max() - df[x].min()) / bins
        fig = px.histogram(df, x=x, title=title)
        if vlines is not None:
            for line in vlines:
                fig.add_vline(x=line)
        fig.update_traces(xbins=dict( # bins used for histogram
                size=bin_size,
            ))
        fig.update_layout(font=dict(size=font_size))
        title = re.sub("[^A-Za-z0-9]+", "", title)
        plot(fig, filename=f"{title}.html")
