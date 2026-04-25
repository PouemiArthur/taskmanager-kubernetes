Task Manager application containerized and orchestrated using Kubernetes

Overview: The NoDownTime task manager app is containerized task manager application by Docker and orchestrated using Kubernetes through a KinD cluster with a control plane and 2 worker nodes. it includes multiple services which include; postgres for database, redis for caching, the backend api, the frontend and Nginx reverse-proxy. Other elements in this project includes locust used for rigorous infrastructure testing.

Architecture: Nginx -> Frontend -> Backend -> Redis -> Postgres

Project structure:

├── backend
│   ├── Dockerfile
│   ├── pjrapp.py
│   ├── requirements.txt
│   └── tests
├── backend-deployment.yaml
├── deployment.yaml
├── deploy.sh
├── expose.txt
├── frontend
│   ├── Dockerfile
│   └── index.html
├── frontend-deployment.yaml
├── locustfile.py
├── nginx
│   ├── Dockerfile
│   └── nginx.conf
├── nginx-deployment.yaml
├── pjr-values.yaml
├── postgres-deployment.yaml
├── pt.txt
├── __pycache__
│   ├── locustfile2.cpython-312.pyc
│   └── locustfile.cpython-312.pyc
├── redis-deployment.yaml
├── service.yaml
├── taskmanager-kub-doc.txt
└── update.sh

 all images of each service is built with Docker using instructions in their respective Dockerfiles and is loaded in the KinD cluster.

Postgres-deployment.yaml:
  - PersistentVolumeClaim: this part requests for persistent storage for the database, in this case 1GB.
  - ConfigMap: the configmap serves for storing critical credentials such as db name and db user. 
  - Secret: this is for storing and hashing absolutely important and sensitive information such as password of the db.
  - StatefulSet: the statefulset is used to manage pods of the db giving it a stable identity and is also the core where the all    the database activity is peformed.
  - VerticalPodAutoscaler: The vertical pod autoscaler requests higher resouce allocation by the db pod(s) in time of high activity
  - Service: service gives stable identity(ip) to db pods for reliable communication with pods of other services also serving as a load balancer to pods under it. 

redis-deployment.yaml:
  - Deployment: it is a pod management tool for redis caching, making sure redis pods are always up and running and also enables live rollbacks and updates.
  - Service: service gives stable identity(ip) to db pods for reliable communication with pods of other services also serving as a load balancer to pods under it.

backend-deployment.yaml:
  - Deployment: it is a pod management tool for backend API pods. making sure backend pods are always up and running and also enables live rollbacks and updates.
  - HorizontalPodAutoscaler: this automatically increases or scales the number of running pods up to 10 preventing the service from crashing in times of high traffic and scale back when traffic goes back to normal.
  - Service: service gives stable identity(ip) to the backend pods for reliable communication with pods of other services also serving as a load balancer to pods under it.

frontend-deployment.yaml:
  - Deployment: this the pod management tool for the frontend interface of the app, making sure frontend pods are always up and running and also enables live rollbacks and updates.
  - Service: service gives stable identity(ip) to frontend pods for reliable communication with pods of other services also serving as a load balancer to pods under it.

nginx-deployment.yaml:
  - Deployment: this the pod management tool for the nginx reverse-proxy serving the frontend and routing requests to the backend, making sure nginx pods are always up and running and also enables live rollbacks and updates.
  - Service: service gives stable identity(ip) to nginx pods for reliable communication with pods of other services also serving as a load balancer to pods under it.

locustfile.py: load testing the system making sure the infrastucture is fit for heavy traffic and activity.
update.sh: script used for faster update from source code to cluser
actions.yml: github actions workflow pipeline for cluster updates with tricy vulnerability image scanner


Note: project files and readme are subject to edits. refer to other projects such as taskmanager-jenkins-docker for readme info on other parts of this project.
