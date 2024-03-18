# Part 1 - Setup Flux and deploy Nautobot to your cluster
Now on to learning how to setup Flux with a k3s cluster and install the Nautobot App. 

## Boot strap FLux 
validate the current context of your Kubectl

```
$ kubectl config current-context
default 
```

create a new github repo for this project

```
flux bootstrap git \
  --url=https://github.com/byrn-baker/nautobot-kubernetes \
  --username=$GITHUB_USERNAME \
  --password=$GITHUB_FLUX_TOKEN \
  --token-auth=true \
  --branch=main \
  --path=clusters/home

► cloning branch "main" from Git repository "https://github.com/byrn-baker/nautobot-kubernetes"
✔ cloned repository
► generating component manifests
✔ generated component manifests
✔ committed component manifests to "main" ("30e10745cea64d0574122d823af1c10670399aa7")
► pushing component manifests to "https://github.com/byrn-baker/nautobot-kubernetes"
✔ reconciled components
► determining if source secret "flux-system/flux-system" exists
► generating source secret
► applying source secret "flux-system/flux-system"
✔ reconciled source secret
► generating sync manifests
✔ generated sync manifests
✔ committed sync manifests to "main" ("feba582d3a766195ea5f12313d4fa3698f2c9e18")
► pushing sync manifests to "https://github.com/byrn-baker/nautobot-kubernetes"
► applying sync manifests
✔ reconciled sync configuration
◎ waiting for GitRepository "flux-system/flux-system" to be reconciled
✔ GitRepository reconciled successfully
◎ waiting for Kustomization "flux-system/flux-system" to be reconciled
✔ Kustomization reconciled successfully
► confirming components are healthy
✔ helm-controller: deployment ready
✔ kustomize-controller: deployment ready
✔ notification-controller: deployment ready
✔ source-controller: deployment ready
✔ all components are healthy
```

You should now see the repo in your cluster
```
$ kubectl get GitRepository -A
NAMESPACE     NAME          URL                                                 AGE   READY   STATUS
flux-system   flux-system   https://github.com/byrn-baker/nautobot-kubernetes   25h   True    stored artifact for revision 'main@sha1:feba582d3a766195ea5f12313d4fa3698f2c9e18'
```

You your ```./clusters/home/flux-system``` folder you should see three files. The kustomization.yaml file will define the files that flux will track as part of the CI/CD definitions and what is being pushed to the cluster.

it should look something like this
```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- gotk-components.yaml
- gotk-sync.yaml
```

You can see the kustomization for flux in the cluster. the ```spec.sourceRef``` defines what repo objects being tracked.
```
$ kubectl get kustomization -n flux-system flux-system -o yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  creationTimestamp: "2024-03-16T17:01:41Z"
  finalizers:
  - finalizers.fluxcd.io
  generation: 1
  labels:
    kustomize.toolkit.fluxcd.io/name: flux-system
    kustomize.toolkit.fluxcd.io/namespace: flux-system
  name: flux-system
  namespace: flux-system
  resourceVersion: "2070912"
  uid: d1cc7b6e-5140-4398-a1d4-058b2ee98081
spec:
  force: false
  interval: 10m0s
  path: ./clusters/home
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
status:
  conditions:
  - lastTransitionTime: "2024-03-17T18:36:35Z"
    message: 'Applied revision: main@sha1:feba582d3a766195ea5f12313d4fa3698f2c9e18'
    observedGeneration: 1
    reason: ReconciliationSucceeded
    status: "True"
    type: Ready
```

## Setting your folder structure to deploy nautobot
Nautobot will require its own kustomization so that we can define what should be tracked as part of our project. In the flux-system folder create a new file and call it ```nautobot-kustomization.yaml```

add the following to the file

```
---
apiVersion: kustomize.toolkit.fluxcd.io/v1beta2
kind: Kustomization
metadata:
  name: nautobot-kustomization
  namespace: flux-system
spec:
  force: false
  interval: 1m0s
  path: ./kubernetes
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
```

We will need to add this to our kustomization.yaml that flux is using so that our nautobot CRDs are tracked as well.

which should look like this

```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- gotk-components.yaml
- gotk-sync.yaml
- nautobot-kustomization.yaml
```

You cluster should be tracking these changes and show the new CRD just created. We have not created the path yet set in the CRD so there is no folder yet to track.
```
$ kubectl get kustomization -n flux-system
NAME                     AGE   READY   STATUS
flux-system              25h   True    Applied revision: main@sha1:9820cde831fc7ab46fef794940cd601a8b73e025
nautobot-kustomization   7s    False   kustomization path not found: stat /tmp/kustomization-602987848/kubernetes: no such file or directory
```

Create a folder that matches the path set forth above. ```./kubernetes```. We will create two files ```./kubernetes/namespace.yaml```, and ```./kubernetes/kustomization.yaml```. kustomization will be used to specify resources, namespace, and configurations for Nautobot and namespace will be used to generate the new namespace for this project.

Checking the clusters Kustomization again you can see the cluster has benn updated. Our Kustomization file is empty, but that will change very soon.

```
$ kubectl get kustomization -n flux-system
NAME                     AGE     READY   STATUS
flux-system              25h     True    Applied revision: main@sha1:83b4c37a23694d646c1593c535834ef6fcb2231d
nautobot-kustomization   8m54s   False   kustomize build failed: kustomization.yaml is empty
```

We will use the [Nautobot HelmChart](https://docs.nautobot.com/projects/helm-charts/en/stable/) to install the Nautobot application, this will be similar to installing this manually via helm and requires similar values as well.

Create a new file ```./kubernetes/nautobot-helmrepo.yaml```. This will define where the HelmChart will be pulled from. Place the following in this file:
```
---
apiVersion: "source.toolkit.fluxcd.io/v1beta2"
kind: "HelmRepository"
metadata:
  name: "nautobot"
  namespace: "nautobot"
spec:
  url: "https://nautobot.github.io/helm-charts/"
  interval: "10m"
```

Create ```./kubernetes/values.yaml``` and place the below in:
```
---
postgresql:
  postgresqlPassword: "SuperSecret123"
redis:
  auth:
    password: "SuperSecret456"
```

We will use the values file to generate a ConfigMap in our cluster, the same method is used if you would deploy this manually with Helm. Update the ```./kubernetes/kustomization.yaml``` to include these new files. This defines how Nautobot will be installed inside the cluster.

It should now look like this
```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: nautobot

resources:
  - namespace.yaml
  - nautobot-helmrepo.yaml

generatorOptions:
  disableNameSuffixHash: true

configMapGenerator:
  - name: "nautobot-values"
    files:
      - "values=values.yaml"
```

Now create a file ```./kubernetes/helmrelease.yaml```. This file defines what HelmChart version to use in the application deployment. The HelmChart defined all of the other dependancy this application requires to run, so we don't have to. Defined below is the charter version, and where it should look for the specific nautobot values we want to define.

```
---
apiVersion: "helm.toolkit.fluxcd.io/v2beta1"
kind: "HelmRelease"
metadata:
  name: "nautobot"
spec:
  interval: "30s"
  chart:
    spec:
      chart: "nautobot"
      version: "1.3.12"
      sourceRef:
        kind: "HelmRepository"
        name: "nautobot"
        namespace: "nautobot"
      interval: "20s"
  valuesFrom:
    - kind: "ConfigMap"
      name: "nautobot-values"
      valuesKey: "values"
```

Be sure to update your ```./kubernetes/kustomization.yaml``` to track these new files. Commit this to your repo, and we should start to see the cluster deploy the application.

We should see that our kustomization in the cluster has been updated

```
$ kubectl get kustomization -n flux-system
NAME                     AGE   READY   STATUS
flux-system              26h   True    Applied revision: main@sha1:ec6b061c699fde8e78ecfb8d92b1e4d183ff53dc
nautobot-kustomization   25m   True    Applied revision: main@sha1:ec6b061c699fde8e78ecfb8d92b1e4d183ff53dc
```

Also we should see helm installing the app
```
$ kubectl get helmreleases -n nautobot
NAME       AGE   READY     STATUS
nautobot   78s   Unknown   Running 'install' action with timeout of 5m0s
```

We should also see that pods have been created in our new nautobot namespace. This takes several minutes as Nautobot has to initialze. We can watch the logs of a given pod with kubectl - ```$ kubectl logs -n nautobot nautobot-58d7fc66f6-5h24f```. You find the pod name with the below command.
```
$ kubectl get pods -n nautobot
NAME                                     READY   STATUS    RESTARTS        AGE
nautobot-58d7fc66f6-5h24f                1/1     Running   3 (2m56s ago)   7m47s
nautobot-58d7fc66f6-tr9l6                1/1     Running   2 (4m26s ago)   7m47s
nautobot-celery-beat-84cf4b547f-v4qq9    1/1     Running   5 (5m21s ago)   7m47s
nautobot-celery-worker-5b9c7648f-6wgdc   1/1     Running   2 (7m5s ago)    7m47s
nautobot-celery-worker-5b9c7648f-c9qzp   1/1     Running   3 (6m49s ago)   7m47s
nautobot-postgresql-0                    1/1     Running   0               7m47s
nautobot-redis-master-0                  1/1     Running   0               7m47s
```

Excelent we have the deployment up and running. We can get further details with ```kubectl describe deployment -n nautobot nautobot```. This will provide details on the docker container version used, along with the exposed ports inside the cluster. Now we need to define how the application can be accessed from outside the cluster.

## How to configure traefik to route requests to Nautobot
In my particular cluster I'm using Traefik as a reverse proxy to my cluster applications. This requires some additional files to define how outside users will be routed to these internal resources. We will need to create two additional files ```./kubernetes/ingress.yaml``` & ```./kubernetes/default-headers.yaml```. 

In the ingress file we will need to tell traefik where it should route requests. This will be done based on the fqdn being requested. On your local DNS server you will want to create an fdqn for natuobot that points at the clusters loadbalancer. 

The ingress.yaml defines what API and kind of configuration to be used in the cluster. We need to provide a name and a namespace as well as the ingress class to be used. The specs outline the entrypoint (typically http/web, or https/websecure) based on your prefrence. Routes define the hostname matching (what does into your browser url) and the services traefik should be routing this request to. Middlewares for our purposes set the type of headers to maintain or adjust depending on your application requirements. 

ingress.yaml:
```
---
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: nautobot
  namespace: nautobot
  annotations:
    kubernetes.io/ingress.class: traefik-external
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`nautobot.local.byrnbaker.me`)
      kind: Rule
      services:
        - name: nautobot
          port: 80
      middlewares:
        - name: default-headers
```

As stated above we will use this to control the headers maintained through traefik. 
default-headers.yaml:
```
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: default-headers
  namespace: nautobot
spec:
  headers:
    browserXssFilter: true
    contentTypeNosniff: true
    customFrameOptionsValue: SAMEORIGIN
    customRequestHeaders:
      X-Forwarded-Proto: https
    forceSTSHeader: true
    stsIncludeSubdomains: true
    stsPreload: true
    stsSeconds: 15552000
```
We need to make sure these are being tracked with flux, so update the resources list in ```./kubernetes/kustomization.yaml``` with these two new files. Commit your changes and in a few minutes we should be able to see the updates pushed down to the cluster. 

We can see flux reconciling the new commit
```
$ kubectl get kustomization -n flux-system
NAME                     AGE   READY     STATUS
flux-system              26h   Unknown   Reconciliation in progress
nautobot-kustomization   68m   True      Applied revision: main@sha1:7c4a8a579e1025a02a6c927d5ffeabce562b2f64
ubuntu@ubuntu-2204-server:~/nautobot-kubernetes$ kubectl get kustomization -n flux-system
NAME                     AGE   READY   STATUS
flux-system              26h   True    Applied revision: main@sha1:7c4a8a579e1025a02a6c927d5ffeabce562b2f64
nautobot-kustomization   69m   True    Applied revision: main@sha1:7c4a8a579e1025a02a6c927d5ffeabce562b2f64
```

We can see the new ingressroute in our namespace
```
$ kubectl get ingressroute -n nautobot
NAME       AGE
nautobot   18m
```

Here we can see some more details if we describe it. This should match what we placed inside of our ingress.yaml file.
```
$ kubectl describe ingressroute nautobot -n nautobot
Name:         nautobot
Namespace:    nautobot
Labels:       kustomize.toolkit.fluxcd.io/name=nautobot-kustomization
              kustomize.toolkit.fluxcd.io/namespace=flux-system
Annotations:  kubernetes.io/ingress.class: traefik-external
API Version:  traefik.containo.us/v1alpha1
Kind:         IngressRoute
Metadata:
  Creation Timestamp:  2024-03-17T19:41:15Z
  Generation:          2
  Resource Version:    2132422
  UID:                 06d1b726-689a-47a2-bd71-8e63e0060071
Spec:
  Entry Points:
    websecure
  Routes:
    Kind:   Rule
    Match:  Host(`nautobot.local.byrnbaker.me`)
    Middlewares:
      Name:  default-headers
    Services:
      Name:  nautobot
      Port:  80
Events:      <none>
```
browsing to our defined fqdn should allow you to access your nautobot app.

When defining our values we did not specify any login credentials for this application. Those have been defined for us and here is how you can retrieve them.

## How to get the generated admin password and API token
```
echo Username: admin
  echo Password: $(kubectl get secret --namespace nautobot nautobot-env -o jsonpath="{.data.NAUTOBOT_SUPERUSER_PASSWORD}" | base64 --decode)
  echo api-token: $(kubectl get secret --namespace nautobot nautobot-env -o jsonpath="{.data.NAUTOBOT_SUPERUSER_API_TOKEN}" | base64 --decode)
```