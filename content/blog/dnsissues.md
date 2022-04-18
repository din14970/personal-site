Title: Fixing slow internet connections due to DNS configuration in Linux
Date: 2021-09-29 13:40
Category: Linux
Tags: DNS, internet, networking, Linux, Telenet
Summary: Slow connections may be due to improperly configured NetworkManager DNS

I have been dealing with an issue recently whereby if I want to browse to a website, say `google.com`, I get excruciatingly slow connection times.
Once I do manage to connect to the site there is no issue whatsoever, and internet speeds are fast.
Following a link, I again get very slow connections.
I get the same behavior with `ping google.com`: exceedingly long times between pings but very fast responses.

This indicated to me there was something wrong with the resolution of domains, and indeed if I tried to ping an IP address directly, say the router at `ping 192.168.0.1` I got very fast pings.
Researching the topic, it seems there could be many possible issues at play, see [here](https://serverfault.com/questions/791911/centos-extremely-slow-dns-lookup#791920) and [here](https://www.math.tamu.edu/~comech/tools/linux-slow-dns-lookup/) and [here](https://serverfault.com/questions/978557/ping-is-very-slow-to-start-if-hostname-is-provided-even-though-dns-resolution-ha).
In my case, it seems related to the `/etc/resolv.conf` file is normally automatically managed by NetworkManager.
The issue seems to pop up whenever I have connected to a VPN provided and disconnected again.
It seems this modifies the resolv file, adding a server entry to which I can obviously no longer connect after disconnecting the VPN.
After disconnecting, it seems the entry is not removed.
Therefore whenever I try to resolve a name, it will try this nameserver, wait a few seconds until time-out before moving on to the next entry, yielding very slow connection times.

While it is not generally recommended, I could solve the issue by editing the `resolv.conf` file and commenting out this first `nameserver` entry.
Restarting the computer automatically resets `resolv.conf`.
To fix this issue permanently, adding `dns=none` to `/etc/NetworkManager/NetworkManager.conf` seems to do the trick.
