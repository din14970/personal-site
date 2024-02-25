Title: Accessing your home server outside your local network
Date: 2024-02-25 13:40
Category: networking
Tags: ssh, socks5, proxy, remote access, network, dynamic dns
Summary: How to access your home network and services running there

I have a small raspberry Pi server at home that runs a few services like gitea (my own personal github alternative) and nextcloud (my own self-hosted google drive alternative).
Self hosting teaches you a lot about how things on the internet work under the hood, and gives you a sense of power since you are fully in control of the services you run.
The annoying thing is that it is very easy to expose services on a local network, but not so trivial to securely expose them to the outside world.
That makes file servers and git repository servers a lot less useful: I have to be at home to have access.
Here I describe the steps I took.

# Configuring port forwarding on the modem/router
I have a very shitty locked down router that is built into the modem provided by my ISP.
I can't even configure a custom DNS (which is a problem as I like to work with pi.hole), and settings are only accessible through an online portal; they are not accessible from the LAN!
In any case, I luckily was able to set up port forwarding.
If you have a decent router, you can probably access the settings at 192.168.0.1.

The modem is the gateway to the internet.
It acts as a first middle man between all devices connected to the home network and the internet.
The IP address that is seen by websites I visit, is the IP address of the modem assigned by the IP address.
If I want to connect to my home network from outside, I need to know this IP address.

But if I have a service running on a raspberry pi, I can not connect to this service directly from outside my home, as this device only has an IP address inside the network (192.168.x.x).
Port forwarding on the modem/router, allows me to connect to services inside the network.
Each modem/router will have different options menus, but in all of them you will have to define:

* internal IP address (e.g. of the Raspberry Pi)
* external port range
* internal port

So, suppose I want to be able to SSH to my Pi, then the internal port is 22.
The external port range is anything I want outside the protected ports.
For example, I could choose 12345:12345 (range of a single port).
Then accessing my external IP on port 12345 will be forwarded to the SSH port on the raspberry pi.
We could then connect with

```bash
ssh <pi username>@<external ip> -p 12345
```

Exposing services to the outside is not without risk.
To improve your security, there are a few things you can do:

* don't expose the default SSH port 22 to the outside. There are bots on the internet constantly trying to connect with SSH on port 22. If your settings are secure then this is not a huge problem, but you will see much less bot activity if you choose a non-default port.
* don't allow password login. Only allow login via SSH key.
* don't allow root login. Only allow SSH via a non-privileged user. Of course this only helps if sudo requires a password.

The first setting is chosen in the port-forwarding settings of the router.
The last two settings are in the `/etc/ssh/sshd_config` file on the server you want to connect to, in my case the raspberry pi.
If you edit this file, restart sshd with `systemctl restart sshd` for the settings to take effect.

# Configure dynamic DNS
One problem of connecting to services inside your home network is that the IP address of your modem is not static.
The ISP may change this on an irregular basis.
Effectively you have a dynamic IP, which is not great if you want to reliably connect to it from outside.

The solution is using a dynamic IP service.
I personally went with [duckdns](www.duckdns.org) as it's free and simple.
You register an account with e.g. your Github account.
Then you can add up to 5 domains, which will be a subdomain of `duckdns.org`.
By default, this will link to the IP you currently connect with, so your home IP.
Like any DNS provider, duckdns will ensure that `mysubdomain.duckdns.org` refers to the IP address of your home network.
That means you can instead use

```bash
ssh -4 <pi username>@mysubdomain.duckdns.org -p 12345
```

Duckdns also registers IPv6 and by default refers to this IP address.
However, I couldn't get the SSH command to work this way, so the -4 serves to force IPv4.

As long as the DNS record points to our home IP we don't have to worry about what the IP is of our home network.
But how does Duckdns know that our IP changes?

This is actually done through the DuckDNS API.
Basically, on the raspberry pi we set up a cronjob to ping duckdns every 5 minutes.
Through the token duckdns generates, it knows where the call comes from, and in this way is able to keep the DNS record in sync with the changing IP address.
In principle, our service will not be available for at most 5 minutes.

# Connecting to other services

Now that we can reliably SSH to our home network, how do we access services like gitea and nextcloud?
As I wrote in another article, we can use the tunnel trick.

```bash
ssh -4 <pi username>@mysubdomain.duckdns.org -p 12345 -N -D 9099
```

This binds the SSH tunnel to port 9099 on the client.
We can use this as a proxy for all kinds of other connections.

For example, to access web interfaces, we can use a browser plug-in like SwitchyOmega to use `SOCKS5://localhost:9099` as proxy host.
You can also configure this plugin so that only specific domains are redirected through the proxy.
Traffic that is proxied is sent through the SSH tunnel and to the raspberry pi, allowing us to access services that are also available on the pi.

I also have pi.hole installed on my raspberry pi, which allows me to configure local DNS records in my home network.
So basically, I have `gitea.rpi4.home.local` configured to point to the internal IP of my raspberry pi.
Devices on my network are configured to use the Pi as DNS name server (normally you would consider this in your router, but I can not).
To ensure the Pi also uses itself as nameserver, we add it in `/etc/resolv.conf`.

```
nameserver <internal IP of the raspberry pi>
```

When I am connected with the SSH tunnel, and have the proxy plugin active in the browser, I can then browse to my home services as if I'm at home.

# Alternatives

It should also be possible to set up a VPN server on the Pi, and use a VPN client to connect to it.
This would avoid some of the hassle with SSH tunnels.
I have not looked into this option but might in the future.

It is also possible to port-forward all the services I want to expose directly on the router.
This is more convenient, but is generally less secure, as each application can be a potential attack vector when exposed to the outside.
Also, typically HTTPS is not configured on services running on the home network, so when exposing them to the outside you will need to set up TLS certificates to encrypt your traffic.
