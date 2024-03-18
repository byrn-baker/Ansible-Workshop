# Deploying Nautobot on Kubernetes
I am joining the #100DayOfHomeLab challenge and as part of this effort I am going to use that time to teach myself something new. 

I love the [Nautobot](https://networktocode.com/nautobot/) and use it all the time at home and at work. I have always deployed this on a standard ubuntu VM, but recently I started to gain interest in deploying it with docker while learning how to create a Nautobot Application. This lead me to looking at Kubernetes and watching a lot of youtube videos on setting up kubernetes. Now I wondered how can I deploy nautobot inside my k3s cluster? Fortunatly there are examples out there and so I stand on the shoulders of those who have figured this all for me. 

For great walk throughs on k3s, traefik, metallb and deploying your cluster with ansible have a look [here](https://github.com/techno-tim/k3s-ansible), and for flux check [this](https://www.youtube.com/watch?v=PFLimPh5-wo) out.

For the original content to the majority of my walk through check out this blog series from networktocode - [part 1](https://blog.networktocode.com/post/deploying-nautobot-to-kubernetes-01/), [part 2](https://blog.networktocode.com/post/deploying-nautobot-to-kubernetes-02/), and [part 3](https://blog.networktocode.com/post/deploying-nautobot-to-kubernetes-03/)

[Part 1 - Setup Flux and deploy Nautobot to your cluster](nautobot-kubernetes_part01.md)

[Part 2 - Creating your own custom container](nautobot-kubernetes_part02.md)