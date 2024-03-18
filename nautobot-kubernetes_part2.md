# Part 2 - Creating your own custom container
There are a lot of great Nautobot apps that compliment and extend the usefullness of Nautobot, and I want to include some of those into my deployment. First lets create a new container of our own based on the nautobot base image.

We need a Dockerfile:
```
ARG NAUTOBOT_VERSION=2.1.5
ARG PYTHON_VERSION=3.11
FROM ghcr.io/nautobot/nautobot:${NAUTOBOT_VERSION}-py${PYTHON_VERSION}
```

Then we can build a new container
```
$ docker build -t ghcr.io/byrn-baker/nautobot-kubernetes:dev .
[+] Building 53.0s (6/6) FINISHED                                                                                                                                                                                                                                                                                                                      docker:default
 => [internal] load build definition from Dockerfile                                                                                                                                                                                                                                                                                                             0.0s
 => => transferring dockerfile: 157B                                                                                                                                                                                                                                                                                                                             0.0s
 => [internal] load metadata for ghcr.io/nautobot/nautobot:1.4.2-py3.9                                                                                                                                                                                                                                                                                           6.7s
 => [auth] nautobot/nautobot:pull token for ghcr.io                                                                                                                                                                                                                                                                                                              0.0s
 => [internal] load .dockerignore                                                                                                                                                                                                                                                                                                                                0.1s
 => => transferring context: 2B                                                                                                                                                                                                                                                                                                                                  0.0s
 => [1/1] FROM ghcr.io/nautobot/nautobot:1.4.2-py3.9@sha256:59f4d8338a1e6025ebe0051ee5244d4c0e94b0223079f806eb61eb63b6a04e62                                                                                                                                                                                                                                    46.0s
 => => resolve ghcr.io/nautobot/nautobot:1.4.2-py3.9@sha256:59f4d8338a1e6025ebe0051ee5244d4c0e94b0223079f806eb61eb63b6a04e62                                                                                                                                                                                                                                     0.0s
 => => sha256:b94fc7ac342a843369c0eaa335613ab9b3761ff5ddfe0217a65bfd3678614e22 11.59MB / 11.59MB                                                                                                                                                                                                                                                                 0.9s
 => => sha256:e262aa54edc9b180deacc4ca2f74512239dd29c964d720431f590674913040b7 4.09kB / 4.09kB                                                                                                                                                                                                                                                                   0.0s
 => => sha256:7a6db449b51b92eac5c81cdbd82917785343f1664b2be57b22337b0a40c5b29d 31.38MB / 31.38MB                                                                                                                                                                                                                                                                 1.7s
 => => sha256:e238bceb29579b6804c25c4e8c81612003af698ef4ca42c46fa87d4ef371653c 1.08MB / 1.08MB                                                                                                                                                                                                                                                                   0.7s
 => => sha256:59f4d8338a1e6025ebe0051ee5244d4c0e94b0223079f806eb61eb63b6a04e62 743B / 743B                                                                                                                                                                                                                                                                       0.0s
 => => sha256:a53d88893414ba30c40c2405436b8c0e2235c7af779506fcb0538cf6534c1ae4 12.49kB / 12.49kB                                                                                                                                                                                                                                                                 0.0s
 => => sha256:aa1ba22295b5c00526e5e18298d5003125b2681e3482b2b7816972597d657ab9 233B / 233B                                                                                                                                                                                                                                                                       0.9s
 => => sha256:76b791f9be0ae4e2896a833164996db3d30fc5f11ee3ccc6fead21577df3d1c5 3.18MB / 3.18MB                                                                                                                                                                                                                                                                   1.5s
 => => sha256:af87da8d87840f333266d174a8ba3a95c32c10e2d728788e8bc38583a7cbaab3 44.99MB / 44.99MB                                                                                                                                                                                                                                                                 3.2s
 => => sha256:25d669acda2475d375d839afc5a3e7ef05670b8ea717f46a4a6b3179365a1687 143B / 143B                                                                                                                                                                                                                                                                       1.7s
 => => extracting sha256:7a6db449b51b92eac5c81cdbd82917785343f1664b2be57b22337b0a40c5b29d                                                                                                                                                                                                                                                                        4.6s
 => => sha256:662197511b86dd33a615825def54fb205daf861d45e7f4a8457c942f79dac86b 1.44kB / 1.44kB                                                                                                                                                                                                                                                                   1.9s
 => => sha256:26c97d3816cf7c585a1fab918a6c7d74fb9094d755d37f6674f318569a86b479 60.32MB / 60.32MB                                                                                                                                                                                                                                                                 4.8s
 => => sha256:dda97b4f6f26d4fc347fbb6ad9c7b33f8ef3ab1e919b6b0e7731de3cc3f04f5e 2.35kB / 2.35kB                                                                                                                                                                                                                                                                   2.1s
 => => sha256:83f2a5cdac6141b5dd64c7e145450c47be3d397c9fe8028109b1dde8698867c8 48.67MB / 48.67MB                                                                                                                                                                                                                                                                 4.5s
 => => sha256:f466dd551ea2aafdf62754b1fa9586776878e1f482af406aaed4f3143011a1e3 49.85MB / 49.85MB                                                                                                                                                                                                                                                                 6.2s
 => => sha256:865e1c397b557f98dfa2a45e7912d3b6552d275a375e616580404b8fabc3706d 1.31kB / 1.31kB                                                                                                                                                                                                                                                                   5.0s
 => => sha256:87c787bcec6ffa56d67767c16a20f360822258fb768af4590eeb8c32a4c471ba 3.67kB / 3.67kB                                                                                                                                                                                                                                                                   5.0s
 => => sha256:27faeb65e5025ce8adf3e7ccb7436f0805ec8535d7709706a7caa170bca9251d 7.48kB / 7.48kB                                                                                                                                                                                                                                                                   5.2s
 => => sha256:7c8ffb49c0dfcc5c41591631a49ecfc73def1ef11e99409a5dac22675725687d 499B / 499B                                                                                                                                                                                                                                                                       5.2s
 => => sha256:8a4f3d60582c68bbdf8beb6b9d5fe1b0d159f2722cf07938ca9bf290dbfaeb6e 5.00kB / 5.00kB                                                                                                                                                                                                                                                                   5.4s
 => => sha256:4f4fb700ef54461cfa02571ae0db9a0dc1e0cdb5577484a6d75e68dc38e8acc1 32B / 32B                                                                                                                                                                                                                                                                         5.3s
 => => extracting sha256:e238bceb29579b6804c25c4e8c81612003af698ef4ca42c46fa87d4ef371653c                                                                                                                                                                                                                                                                        0.4s
 => => extracting sha256:b94fc7ac342a843369c0eaa335613ab9b3761ff5ddfe0217a65bfd3678614e22                                                                                                                                                                                                                                                                        1.4s
 => => extracting sha256:aa1ba22295b5c00526e5e18298d5003125b2681e3482b2b7816972597d657ab9                                                                                                                                                                                                                                                                        0.0s
 => => extracting sha256:76b791f9be0ae4e2896a833164996db3d30fc5f11ee3ccc6fead21577df3d1c5                                                                                                                                                                                                                                                                        0.9s
 => => extracting sha256:af87da8d87840f333266d174a8ba3a95c32c10e2d728788e8bc38583a7cbaab3                                                                                                                                                                                                                                                                        5.9s
 => => extracting sha256:25d669acda2475d375d839afc5a3e7ef05670b8ea717f46a4a6b3179365a1687                                                                                                                                                                                                                                                                        0.0s
 => => extracting sha256:662197511b86dd33a615825def54fb205daf861d45e7f4a8457c942f79dac86b                                                                                                                                                                                                                                                                        0.0s
 => => extracting sha256:26c97d3816cf7c585a1fab918a6c7d74fb9094d755d37f6674f318569a86b479                                                                                                                                                                                                                                                                       23.6s
 => => extracting sha256:dda97b4f6f26d4fc347fbb6ad9c7b33f8ef3ab1e919b6b0e7731de3cc3f04f5e                                                                                                                                                                                                                                                                        0.0s
 => => extracting sha256:83f2a5cdac6141b5dd64c7e145450c47be3d397c9fe8028109b1dde8698867c8                                                                                                                                                                                                                                                                        0.9s
 => => extracting sha256:f466dd551ea2aafdf62754b1fa9586776878e1f482af406aaed4f3143011a1e3                                                                                                                                                                                                                                                                        3.2s
 => => extracting sha256:87c787bcec6ffa56d67767c16a20f360822258fb768af4590eeb8c32a4c471ba                                                                                                                                                                                                                                                                        0.0s
 => => extracting sha256:865e1c397b557f98dfa2a45e7912d3b6552d275a375e616580404b8fabc3706d                                                                                                                                                                                                                                                                        0.0s
 => => extracting sha256:7c8ffb49c0dfcc5c41591631a49ecfc73def1ef11e99409a5dac22675725687d                                                                                                                                                                                                                                                                        0.0s
 => => extracting sha256:27faeb65e5025ce8adf3e7ccb7436f0805ec8535d7709706a7caa170bca9251d                                                                                                                                                                                                                                                                        0.0s
 => => extracting sha256:4f4fb700ef54461cfa02571ae0db9a0dc1e0cdb5577484a6d75e68dc38e8acc1                                                                                                                                                                                                                                                                        0.0s
 => => extracting sha256:8a4f3d60582c68bbdf8beb6b9d5fe1b0d159f2722cf07938ca9bf290dbfaeb6e                                                                                                                                                                                                                                                                        0.0s
 => exporting to image                                                                                                                                                                                                                                                                                                                                           0.0s
 => => exporting layers                                                                                                                                                                                                                                                                                                                                          0.0s
 => => writing image sha256:d9a37159279f8bd77a47ab44b51408267312c70c84552556eb71456843d89bea                                                                                                                                                                                                                                                                     0.0s
 => => naming to ghcr.io/byrn-baker/nautobot-kubernetes:dev
```

We have our new image created:
```
$ docker image ls
REPOSITORY                               TAG       IMAGE ID       CREATED         SIZE
ghcr.io/byrn-baker/nautobot-kubernetes   dev       d9a37159279f   18 months ago   580MB
```

A Makefile can be used to simplify the building, pushing, and pulling of new version of this container as we progress.

```
# Get current branch by default
tag := $(shell git rev-parse --abbrev-ref HEAD)

build:
	docker build -t ghcr.io/byrn-baker/nautobot-kubernetes:$(tag) .

push:
	docker push ghcr.io/byrn-baker/nautobot-kubernetes:$(tag)

pull:
	docker pull ghcr.io/byrn-baker/nautobot-kubernetes:$(tag)
```

Test the Building and Pushing with your Makefile:

```
$ make build
docker build -t ghcr.io/byrn-baker/nautobot-kubernetes:main .
[+] Building 1.1s (6/6) FINISHED                                                                                                                                                                                                                                                                                                                       docker:default
 => [internal] load build definition from Dockerfile                                                                                                                                                                                                                                                                                                             0.0s
 => => transferring dockerfile: 157B                                                                                                                                                                                                                                                                                                                             0.0s
 => [internal] load metadata for ghcr.io/nautobot/nautobot:1.4.2-py3.9                                                                                                                                                                                                                                                                                           0.9s
 => [auth] nautobot/nautobot:pull token for ghcr.io                                                                                                                                                                                                                                                                                                              0.0s
 => [internal] load .dockerignore                                                                                                                                                                                                                                                                                                                                0.0s
 => => transferring context: 2B                                                                                                                                                                                                                                                                                                                                  0.0s
 => CACHED [1/1] FROM ghcr.io/nautobot/nautobot:1.4.2-py3.9@sha256:59f4d8338a1e6025ebe0051ee5244d4c0e94b0223079f806eb61eb63b6a04e62                                                                                                                                                                                                                              0.0s
 => exporting to image                                                                                                                                                                                                                                                                                                                                           0.0s
 => => exporting layers                                                                                                                                                                                                                                                                                                                                          0.0s
 => => writing image sha256:d9a37159279f8bd77a47ab44b51408267312c70c84552556eb71456843d89bea                                                                                                                                                                                                                                                                     0.0s
 => => naming to ghcr.io/byrn-baker/nautobot-kubernetes:main
 ```

 ```
$ make push
docker push ghcr.io/byrn-baker/nautobot-kubernetes:main
The push refers to repository [ghcr.io/byrn-baker/nautobot-kubernetes]
3cec5ea1ba13: Mounted from nautobot/nautobot 
5f70bf18a086: Mounted from byrn-baker/nautobot-k3s 
4078cbb0dac2: Mounted from nautobot/nautobot 
28330db6782d: Mounted from nautobot/nautobot 
46b0ede2b6bc: Mounted from nautobot/nautobot 
f970a3b06182: Mounted from nautobot/nautobot 
50f757c5b291: Mounted from nautobot/nautobot 
34ada2d2351f: Mounted from nautobot/nautobot 
2fe7c3cac96a: Mounted from nautobot/nautobot 
ba48a538e919: Mounted from nautobot/nautobot 
639278003173: Mounted from nautobot/nautobot 
294d3956baee: Mounted from nautobot/nautobot 
5652b0fe3051: Mounted from nautobot/nautobot 
782cc2d2412a: Mounted from nautobot/nautobot 
1d7e8ad8920f: Mounted from nautobot/nautobot 
81514ea14697: Mounted from nautobot/nautobot 
630337cfb78d: Mounted from nautobot/nautobot 
6485bed63627: Mounted from nautobot/nautobot 
main: digest: sha256:122f9ddd54ba67893c5292986f1c5433b3c1ce2ba651c76e7732631ee5776178 size: 4087
 ```

Now lets see if we can deploy this custom image to our cluster. We need to update the values.yaml with our custom image registery and repo information. You will need to create a secret for your repo so that it can be pulled as part of the CI/CD workflow. You can find this under the repo settings and secrets, your personal access token can be placed there.
```
nautobot:
  image:
    registry: "ghcr.io"
    repository: "byrn-baker/nautobot-kubernetes"
    tag: "main"
    pullSecrets:
      - "ghcr.io"
```
We can also add this secret to our cluster as well. 
```
$ kubectl create secret docker-registry --docker-server=ghcr.io --docker-username=byrn-baker --docker-password=$GITHUB_FLUX_TOKEN -n nautobot ghcr.io
secret/ghcr.io created
```
Update the helm chart being used in the ```./kubernetes/helmrelease.yaml``` file to the latest version 2.0.5 and makesure that we have the nautobot-ingress described as a ConfigMap with the values pointed to our ingress. You will also need to update the posgresql password key in the ```./kubernetes/values.yaml``` so that it follows this structure - ```postgresql.auth.password```. We will also want to update ```./kubernetes/ingress.yaml``` under routes.services make sure the name is ```nautobot-default```, as this new version changes the name of the service we are trying to match. 

Now commit and push the changes to your repo.

Should see the nautobot pods restarting now, and after a few minutes it should finish initializing.
```
$ kubectl get pods -n nautobot
NAME                                     READY   STATUS    RESTARTS        AGE
nautobot-5b65b45bd8-5lnhj                0/1     Running   3 (20s ago)     5m11s
nautobot-5b65b45bd8-qx4c6                0/1     Running   3 (20s ago)     5m11s
nautobot-celery-beat-79cb85b4df-8k6dk    1/1     Running   1 (4m34s ago)   5m11s
nautobot-celery-worker-8968d5477-jspgp   1/1     Running   0               4m2s
nautobot-celery-worker-8968d5477-vpktd   1/1     Running   0               5m11s
nautobot-postgresql-0                    1/1     Running   0               8h
nautobot-redis-master-0                  1/1     Running   0               8h
```

We can also see that the image being used was pulled from our repo
```
$ kubectl describe pod -n nautobot nautobot-5b65b45bd8-5lnhj | grep Image
    Image:          ghcr.io/byrn-baker/nautobot-kubernetes:main
```

If you notice that the nautobot containers are not fully booting and going through a reboot cycle because of a livelyness checking failing. Check to see if the helm install completed succesfully
```
$ kubectl get helmreleases -n nautobot
NAME       AGE   READY   STATUS
nautobot   25h   False   Helm upgrade failed for release nautobot/nautobot with chart nautobot@1.3.14: context deadline exceeded
```
I ran into an odd issue where the container did not want to update from the networktocode to my customer container. So I uninstalled the deployment ```helm uninstall -n nautobot nautobot```. To have flux install it again run ```flux reconcile helmrelease nautobot -n nautobot```, which tell the cluster to pull the latest commit from the repo and this should fire up the pods for nautobot.

```
$ kubectl get pods -n nautobot
NAME                                       READY   STATUS    RESTARTS      AGE
nautobot-celery-beat-689f8b6df8-m8gxn      1/1     Running   0             65m
nautobot-celery-default-6b558d5484-gc2lf   1/1     Running   1 (65m ago)   65m
nautobot-celery-default-6b558d5484-p6cfp   1/1     Running   1 (65m ago)   65m
nautobot-default-79f9b4f674-55vln          1/1     Running   0             65m
nautobot-default-79f9b4f674-vm9hc          1/1     Running   0             65m
nautobot-postgresql-0                      1/1     Running   0             65m
nautobot-redis-master-0                    1/1     Running   0             65m
```

We now have the most recent nautobot deployed from our own custom image on our repo.

```
$ kubectl get pods -n nautobot
Image:         ghcr.io/byrn-baker/nautobot-kubernetes:main
```

<img src="/assets/images/kubernetes/nautobot-2.1.5.png" alt="">

