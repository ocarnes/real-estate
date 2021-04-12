# README
## GKE Commands ##
Build docker image of scraper
```
docker build -t zillow_scraper .
```
Tag container with a GCR uri
```
docker tag zillow_scraper gcr.io/plenary-era-308716/zillow_scraper
```
Push container to Google Container Registry (GCR)
```
docker push gcr.io/plenary-era-308716/zillow_scraper
```
Create Google Kubernetes Engine (GKE) cluster
```
gcloud container clusters create zillow-scraper-cluster --zone us-central1-f --machine-type=n1-standard-1 --max-nodes=5 --min-nodes=1
```
Add credentials to cluster
```
kubectl create secret generic cloudsql-instance-credentials --from-file=sql_credentials.json=<service_account_json_file>

kubectl create secret generic cloudsql-db-credentials --from-literal=username=[DB_USER] --from-literal=password=[DB_PASS] --from-literal=dbname=[DB_NAME]

gcloud container clusters get-credentials zillow-scraper-cluster --zone us-central1-f
```

Add container from GCR to GKE
```
kubectl create -f zillow_scraper.yaml
```
## Error Inspection ##
Inspect container
```
kubectl get pods
```
Check container logs to see any errors present
```
kubectl logs zillow-scraper-8566db5bf7-p9xs8 zillow-scraper
```
Scale down to zero replicas
```
kubectl scale --replicas=0 -f zillow_scraper.yaml
```
## Removing Everything ##
Delete GKE clusters
```
gcloud container clusters delete zillow-scraper-cluster --region=us-central1-f
```
Delete image
```
gcloud container images delete gcr.io/plenary-era-308716/zillow_scraper
```
