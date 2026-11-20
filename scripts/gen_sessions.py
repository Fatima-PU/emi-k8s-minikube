import random, sys
rate = int(sys.argv[1]); secs = int(sys.argv[2]); out = sys.argv[3]
with open(out, "w") as f:
    for _ in range(min(rate * secs, 900)):
        p = random.randrange(10000, 1000001, 1000)
        r = round(random.uniform(5, 20), 1)
        n = random.randint(6, 60)
        f.write("/api/emi method=POST contents='{\"P\":%d,\"rate\":%s,\"n\":%d}'\n\n" % (p, r, n))
