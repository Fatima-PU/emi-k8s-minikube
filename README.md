# Loan EMI Calculator on Kubernetes (Minikube)

Flask + MongoDB (3-member replica set) app deployed on Minikube with NGINX Ingress, load tests and HPA.

## Layout
- `app/` : Flask app, Dockerfile, .dockerignore
- `k8s/` : all manifests (namespace, MongoDB StatefulSet, mongo-init Job, ConfigMap, web Deployment+Service, Ingress, HPA)
- `scripts/` : load-test, sampler and plotting scripts
- `results/` : raw outputs (httperf outputs, CSVs, logs) and graphs

## Bring up on a fresh Minikube
```bash
minikube start
minikube addons enable ingress
minikube addons enable metrics-server

cd app && docker build -t emi-web:1.0 . && minikube image load emi-web:1.0 && cd ..

kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-mongo.yaml
kubectl wait --for=condition=ready pod/mongo-0 pod/mongo-1 pod/mongo-2 -n emi --timeout=300s
kubectl apply -f k8s/02-mongo-init.yaml
kubectl apply -f k8s/03-configmap.yaml
kubectl apply -f k8s/04-web.yaml
kubectl apply -f k8s/05-ingress.yaml
```
(`kubectl apply -f k8s/` also works, but the mongo-init Job may need a retry if MongoDB pods are not ready yet.)

Add the host entry: `echo "$(minikube ip) emi.local" | sudo tee -a /etc/hosts`, then open http://emi.local

## HPA (autoscaling test only)
```bash
kubectl apply -f k8s/06-hpa.yaml
```
Do not apply it during the fixed-replica load tests.

## Load tests
```bash
cd scripts
./run_tests.sh      # 15 runs (1,2,3 replicas x 10,25,50,100,200 req/s)
./run_hpa.sh        # 10-minute autoscaling test
python3 plot12.py   # graphs 1 and 2
python3 plot3.py    # graph 3
```
Requires httperf, python3-matplotlib and python3-pandas.
