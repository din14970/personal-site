Title: Setting up a K8s cluster with kubeadm on a Debian 11 Bullseye laptop
Date: 2022-10-11 13:40
Category: DevOps
Tags: kubernetes, K8s, containers, ssh, flannel, containerd
Summary: The particularities of setting up a K8s cluster with kubeadm on a laptop


Setting up a local K8s cluster for playing around is pretty easy.
You can choose from tools like [minikube](https://minikube.sigs.K8s.io/docs/), [k3s](https://docs.k3s.io/), or [microK8s](https://microK8s.io/) depending on your usecase and get up and running in minutes.
However, it doesn't give you the satisfaction of setting up a "real" cluster that could be used for production (although some of these other tools).
Most of the official K8s documentation deals with kubeadm installs, and also the clusters one deals with for the CKA (Certified Kubernetes Administrator) exam are kubeadm clusters.
I felt like this experience of setting up a cluster with kubeadm was missing from my repertoire.
I had a spare old ASUS laptop laying around with 2 CPU cores and 6 gigs of RAM, which is [just enough for setting up a control plane node](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/) so I thought I would give it a shot on this platform.
While kubeadm installs should be much easier and faster than a true ["from scratch" install](https://www.youtube.com/playlist?list=PL2We04F3Y_41jYdadX55fdJplDvgNGENo), I still ran into quite a few issues which are not explicitly mentioned on [the documentation page that explains how to bootstrap a kubeadm cluster](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/), so I figured I would write this post to detail my process.

### Installing the host OS
The laptop ran Windows 8.
I got Debian 11 from [the website](https://www.debian.org/distrib/netinst) and flashed it onto a spare 1 GB USB drive with `dd`.
Really the main reason I chose Debian over Ubuntu was because the later image was larger than 1 GB.
Then I booted from this USB and just followed the install instructions.
I opted for not installing any graphical environment and used a single partition on the disk.

### Configuring the host OS
As I want to work on this laptop remotely and use it as a server, I installed and configured ssh.
I copied over my public key from my main computer to the `authorized_keys` so I could ssh into the machine.
Some important things I had to manually configure to turn this into a useable server:

* I was using wifi to connect the laptop to the LAN. In Debian this is using NetworkManager. I had to set up a static IP, otherwise it would be impossible to connect reliably via SSH or later the Kubernetes services. In the end I did this using `nmcli` as found [here](https://michlstechblog.info/blog/linux-set-a-static-fixed-ip-with-network-manager-cli/)

```bash
$ sudo nmcli con  # view name of connections
$ sudo nmcli con mod "name-of-connection" \
  ipv4.addresses "<static ip>/<CIDR>" \
  ipv4.gateway "<router ip>" \
  ipv4.dns "8.8.8.8" \
  ipv4.method "manual"
```
* By default if I closed the laptop lid, the laptop went into suspension mode and I could no longer connect with SSH. I followed [this stackexchange thread](https://unix.stackexchange.com/questions/563729/looking-for-the-settings-that-causes-debian-to-suspend-when-laptop-lid-is-closed).
* I want the laptop to automatically log in as root on a reboot on tty1. I followed [this stackexchange thread](https://unix.stackexchange.com/questions/401759/automatically-login-on-debian-9-2-1-command-line).
* For the `kubelet` process, it turns out you can not have `swap` memory enabled (of course I only discovered this at a later stage). During the Debian install process this is automatically created. You can run `sudo swapoff -a` and remove the `swap` related lines in `/etc/fstab`, but to make swap disabling truly persistent across reboots I also had to run `sudo systemctl mask "dev-sda3.swap"`.
* I configured a firewall with `ufw`. A number of ports need to be opened, for which I followed [this guide](https://www.howtoforge.com/how-to-setup-kubernetes-cluster-with-kubeadm-on-debian-11/). This guide also explains how to set up kernel modules `overlay` and `br_netfilter`.

### Installing a container runtime
Many container runtimes can be used with K8s.
Initially I thought I would use docker.
I just followed [the official docs](https://docs.docker.com/engine/install/debian/).
In the end I decided to use `containerd` instead as container runtime, which also gets installed if you follow the docker installation.

### Configuring Containerd
It is very important to configure `containerd` before bootstrapping the cluster.
I did not do this on my first try and ran into all kinds of issues which were difficult to find solutions to.
The details can be found [here](https://kubernetes.io/docs/setup/production-environment/container-runtimes/#containerd).
You need to edit some settings in `/etc/containerd/config.toml`.
The trouble is that by default, installing `containerd` with `apt` does not create this file.
To create the file run

```
# containerd config default > /etc/containerd/config.toml
```

Then, change the appropriate settings to the following:

```
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
  ...
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
    SystemdCgroup = true

...


[plugins."io.containerd.grpc.v1.cri"]
    sandbox_image = "registry.K8s.io/pause:3.8"
```
Also check that `cri` is not in `disabled plugins`.
If the sandbox image is not changed, the various `kube-system` components will get stuck in crash loops, I suppose because their startup is timed incorrectly and their communication gets out of sync.
The version here is the image that was downloaded when I called `kubeadm init` (and failed to bootstrap the cluster).
It will depend on the version of K8s and kubeadm.
In my case, I was installing `v1.25.2`.
You can view the images with 

```
$ sudo crictl images
```

after you have pulled them. 

When you have made your changes, you should restart containerd

```bash
$ sudo systemctl restart containerd
```

There's also a note on setting `systemd` as the `cgroupDriver` for the `kubelet`, but I did not do any special configuration for this and it seems to work.

### Installing components
Here we more or less follow [this page of the docs](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/).

```
$ sudo apt-get update
$ sudo apt-get install -y apt-transport-https ca-certificates curl
$ sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
$ echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
$ sudo apt-get update
$ sudo apt-get install -y kubelet kubeadm kubectl
$ sudo apt-mark hold kubelet kubeadm kubectl
```

You can now check whether the `kubelet` exists as a systemd service, however it should not be active since `kubeadm` has not created configuration for it.

```
$ sudo systemctl status kubelet
```

### Bootstrapping the cluster
Finally we can more or less follow the standard documentation [here](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm), and initialize the cluster with

```
$ sudo kubeadm init \
 --pod-network-cidr=10.244.0.0/16 \
 --cri-socket=/run/containerd/containerd.sock
```

By default, the IP address that will be used for the master node is the one exposed on the LAN, so it is important that this is a static IP (see earlier).

The pod network cidr is specific to the pod network add-on that should be installed afterwards.
I decided to go with [flannel](https://github.com/flannel-io/flannel) for no specific reason other than I saw it often in the clusters that I used for the CKA preparation.

If all goes well, you should get a message that the cluster is now initialized.
If it errors out somewhere, you will likely have the tear down everything with `sudo kubeadm reset`, change some configuration and try again.
To see more in detail what is going on you can check `sudo kubeadm init --v=5`. 
Additional debugging strategies:

* Check [this page](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/troubleshooting-kubeadm/) to see if you find your error. 
* Check the status and logs of the `kubelet` with `sudo systemctl status kubelet` and `sudo journalctl -u kubelet -f`.
* Check if any of the system components were created as containers and their status with `sudo crictl ps`. You can then check logs of individual containers with `sudo crictl logs <container id>`.

### Further configuration
If you get the message that the cluster initialized correctly, you need for your user to get access to the `kube-api-server` by copying a config file to the right location:

```
$ mkdir $HOME/.kube
$ sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
$ sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

You should now have access to the cluster, which you can test with `$ kubectl get pods -A`.
You can now actually copy this same config file to another computer on the LAN, e.g. with `scp` and operate the cluster remotely without having to `ssh` into the master node.
Of course you need `kubectl` installed on the computer as well.

### Installing flannel as pod network plugin
At this point if you check the pods in the `kube-system` namespace, `coredns` should not work as a pod network plugin is required.
To install `flannel` I simply run the command from the github page

```
$ kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
```

If this is successful, there should now be a `flannel` pod in the `kube-flannel` namespace and the `coredns` pods should be running.

### Removing taint controlplane
Normally at this stage you would set up and join worker nodes to the cluster. 
In principle you don't want to run workloads on the control plane, as it could bring down the entire cluster if you run out of resources.
I have another spare laptop which I might set up for this use case at some point, but at the moment I'm content just using a single-node setup.
By default, kubeadm with taint the control-plane node with `NoSchedule` so no pods will actually run on this cluster.
To remove the taint, run

```
$ kubectl taint node <node name> node-role.kubernetes.io/control-plane:NoSchedule-
```

You can then test if you can get a pod up an running

```
$ kubectl run nginx --image=nginx
```

If you can get this pod to run everything should be set up correctly.
