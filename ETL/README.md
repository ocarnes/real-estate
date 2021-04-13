# README
## Useful Links ##
* To run Google Cloud commands locally: [Installing SDK](https://cloud.google.com/sdk/docs/install)
* To query Cloud SQL locally: [Connecting to Cloud Auth Proxy](https://cloud.google.com/sql/docs/postgres/quickstart-proxy-test)

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

kubectl create secret generic cloudsql-db-credentials --from-literal=username=[DB_USER] --from-literal=password=[DB_PASS] --from-literal=dbname=[DB_NAME] --from-literal=sqlhost=[SQL_HOST] --from-literal=dbport=[DB_PORT]

gcloud container clusters get-credentials zillow-scraper-cluster --zone us-central1-f
```
Add container from GCR to GKE
```
kubectl create -f cronjob.yaml
```
## Error Inspection ##
Monitor jobs to see when pods start / if they've run successfully
```
kubectl get jobs --watch
```
Get pod logs to determine issues
```
pods=$(kubectl get pods -l app=zillow-scraper-cron -o jsonpath='{.items[0].metadata.name}')

kubectl logs $pods zillow-scraper

kubectl logs $pods cloud-sql-proxy
```
Inspect container
```
kubectl get pods
```
Scale down to zero replicas
```
kubectl scale --replicas=0 -f zillow_scraper.yaml
```
## Removing Everything ##
Removing cronjob
```
kubectl delete cronjob zillow-scraper-cron
```
Delete GKE clusters
```
gcloud container clusters delete zillow-scraper-cluster --region=us-central1-f
```
Delete image
```
gcloud container images delete gcr.io/plenary-era-308716/zillow_scraper
```
