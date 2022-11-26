Title: Accessing resources in a private network with SSH tunnel proxies
Date: 2022-11-22 13:40
Category: networking
Tags: ssh, socks5, proxy, remote access, network
Summary: How to use SSH tunnels to access private websites, databases, and pull docker images from a host outside the network.


Companies tend to restrict access to internal systems to approved devices on the internal network.
Sometimes one needs or wants to access internal systems from a machine outside the network. 
This can be achieved if you can SSH into a machine that is connected to the internal network and can access the required resources.

### Binding a remote service to a port on localhost
If you are on an internal network and you can access an internal application via a host/IP address + a port, then you can access that resource from outside the network by binding it to a port on `localhost`.

For example, a database may be accessible on some IP `db host` and a port `db port`.
To connect to the database with some client (e.g. dbeaver or SQLAlchemy) inside the network, you would need a connection string of the form `<db type>://<db user>:<db pw>@<db host>:<db port>/<db>`.

Of course if you are outside the internal network, then `db host` can not be resolved.
Instead what you can do is use

```
$ ssh -L <localhost port>:<db host>:<db port> <ssh server user>:<ssh server pw>@<ssh server host>
```

`ssh server` in this case refers to the host to which you can SSH from outside the network.
Of course if you set up SSH access via keys, then `ssh server pw` will not be required.
`locahost port` can be freely chosen, but it must be a port that is not yet in use.

If this command runs successfully, you will be SSHed into the ssh server host, but also the database will be bound to the original host.
On this host, it will then be accessible with the connection string `<db type>://<db user>:<db pw>@localhost:<localhost port>/<db>`.

### Binding the SSH connection to a port
It may be inconvenient to directly bind individual internal services to localhost ports.
For example, you may want to browse multiple internal websites on different hosts.
For this use case, there is another solution: 

```
$ ssh -D <port> <ssh server user>:<ssh server pw>@<ssh server host>
```

This opens the SSH connection and binds it directly to a local `port` of your choosing. 
You can then use `localhost:<port>` with `SOCKS5` as a proxy for various services.
In order to use this proxy, the client application must support proxied connections.
Some examples.

#### Accessing internal websites
Once you have bound the tunnel to a port, you can use it as a proxy in your browser to connect to internal websites.
Most browsers have a built-in feature to allow you to set up a proxy connection, but this can be clunky if you don't always want to connect through this proxy.
A plug-in for easily switching proxies can be helpful, e.g. SwitchyOmega for Firefox.
In SwitchyOmega, you can create a new profile and add a proxy server with protocol=SOCKS5, server= localhost, and port=`<port>`.
You should now be browsing as if you are on the internal network.

#### Pulling docker images from a private image registry
Suppose you need to pull a docker image from a private registry only accessible from inside the internal network.
You can create a file `/etc/systemd/system/docker.service.d/http-proxy.conf`:

```
[Service]
Environment="HTTP_PROXY=socks5://127.0.0.1:<port>"
Environment="HTTPS_PROXY=socks5://127.0.0.1:<port>"
Environment="NO_PROXY=hub.docker.com"
```

Then you should restart the docker daemon

```
# systemctl daemon-reload
# systemctl restart docker
```

Credit to [this stackoverflow answer](https://stackoverflow.com/questions/69047394/cant-pull-docker-image-behind-a-proxy) for guidance on this topic.

Now you can pull the docker image through the tunnel.

### Gaining access to a ssh server host
The ssh server must of course somehow be accessible to your host outside the network.
If the server exists within the network but does not expose the ssh port to the internet you can not connect.
There may be a workaround using a company laptop that can make a VPN connection to the network.
When the VPN is on, the laptop is effectively part of the internal network. 
If an ssh server can be run on the laptop, and it is simultaneously connected via VPN, then you can use the laptop as access point to the internal network.
To make this practical, you should assign the laptop a static IP on your LAN.
Even if the work laptop is running Windows, you can still make it into an ssh server if you have admin privileges; best to google the details.
