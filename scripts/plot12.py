import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = "/home/vboxuser/emi-k8s/results/"

# Graph 1
s = pd.read_csv(R + "summary.csv")
fig, ax = plt.subplots(figsize=(8, 5))
for rep, g in s.groupby("replicas"):
    ax.plot(g["rate"], g["avg_response_ms"], marker="o", label=f"{rep} replica(s)")
ax.set_xlabel("Request rate (req/s)")
ax.set_ylabel("Average response time (ms)")
ax.set_title("Graph 1: Response time vs request rate")
ax.set_yscale("log")
ax.grid(True); ax.legend()
fig.savefig(R + "graph1_response_time.png", dpi=150, bbox_inches="tight")

# Graph 2: per-pod CPU, 100 req/s, 3 replicas
p = pd.read_csv(R + "pods_r3_rate100.csv", parse_dates=["timestamp"])
p = p[p["pod"].str.startswith("emi-web")]
fig, ax = plt.subplots(figsize=(8, 5))
for pod, g in p.groupby("pod"):
    ax.plot(g["timestamp"], g["cpu_m"] / 250 * 100, marker="o", label=pod[-5:])
ax.set_xlabel("Time")
ax.set_ylabel("CPU utilization (% of 250m limit)")
ax.set_title("Graph 2: Per-pod CPU, 100 req/s, 3 replicas")
ax.grid(True); ax.legend()
fig.autofmt_xdate()
fig.savefig(R + "graph2_pod_cpu.png", dpi=150, bbox_inches="tight")
print("done")
