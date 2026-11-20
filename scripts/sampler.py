import sys, time, subprocess, threading, datetime
cpu_file, pod_file = sys.argv[1], sys.argv[2]
now = lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def read():
    v = list(map(int, open('/proc/stat').readline().split()[1:]))
    return v[3] + v[4], sum(v)

def pods():
    with open(pod_file, 'w') as f:
        f.write("timestamp,pod,cpu_m,mem_Mi\n")
        while True:
            ts = now()
            out = subprocess.run(["kubectl","top","pods","-n","emi","--no-headers"],
                                 capture_output=True, text=True).stdout
            for line in out.splitlines():
                p = line.split()
                if len(p) >= 3:
                    f.write(f"{ts},{p[0]},{p[1].rstrip('m')},{p[2].rstrip('Mi')}\n")
            f.flush()
            time.sleep(15)

threading.Thread(target=pods, daemon=True).start()
with open(cpu_file, 'w') as f:
    f.write("timestamp,cpu_percent\n")
    pi, pt = read()
    while True:
        time.sleep(1)
        i, t = read()
        f.write(f"{now()},{100*(1-(i-pi)/(t-pt)):.1f}\n")
        f.flush()
        pi, pt = i, t
