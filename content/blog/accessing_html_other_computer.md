Title: Quick browsing of HTML files on another computer
Date: 2025-08-06 13:40
Category: networking
Tags: ssh, html, remote access, network
Summary: Easy way to browse HTML files on another computer

Consider the following scenario: you are developing a Python package on a remote computer without a screen (e.g. an HPC cluster).
You are working on Sphinx docs for this package.
You build the docs and have some HTML files.
How do you view them?

There are essentially two easy ways.

One is to copy over the entire HTML folder to your machine with `rsync`.
But this is annoying as it requires a copy every time you make a change.
One additional command: too much work.

Another option is to start an HTTP server on the remote machine where the HTML files live and connect to it via SSH.
We can avoid the complexity of Nginx or Apache: Python has such a feature built-in, which is fine for this purpose.
From the `docs` folder, run:

```bash
python3 -m http.server 8080 -d build/html
```

On the machine where you are working, make an SSH tunnel:

```bash
ssh -N -L 8080:127.0.0.1:8080 remote_pc
```

Then open your browser to `http://127.0.0.1:8080` and you can view your docs!
As long as the http server is running, rebuilding the docs will automatically update them.
Just a little thing I found useful in a pinch.
