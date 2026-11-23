import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
R = "/home/vboxuser/emi-k8s/results/"

h = pd.read_csv(R + "hpa_replicas.csv", parse_dates=["timestamp"])
ph = pd.read_csv(R + "hpa_phases.csv", parse_dates=["timestamp"])

fig, axs = plt.subplots(3, 1, sharex=True, figsize=(9, 9))

axs[0].step(ph["timestamp"], ph["rate"], where="post", color="tab:blue")
axs[0].set_ylabel("Request rate (req/s)")
axs[0].set_title("Graph 3: Autoscaling test (17 min)")

c = h.dropna(subset=["avg_cpu_percent"])
axs[1].plot(c["timestamp"], c["avg_cpu_percent"], marker="o", color="tab:orange")
axs[1].axhline(50, color="red", linestyle="--", label="Target 50%")
axs[1].set_ylabel("Avg CPU (% of request)")
axs[1].legend()

axs[2].step(h["timestamp"], h["current_replicas"], where="post", marker="o", color="tab:green")
axs[2].set_ylabel("Web replicas")
axs[2].set_yticks(range(0, 7))
axs[2].set_xlabel("Time")

for a in axs:
    a.grid(True)
axs[2].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
fig.autofmt_xdate()
fig.savefig(R + "graph3_autoscaling.png", dpi=150, bbox_inches="tight")
print("done")
