Title: Setting up cusdis on your server behind nginx to host your own comments
Date: 2021-08-21 13:40
Category: DevOps
Tags: self-hosting, website, cusdis, comments, nginx
Summary: Here I go through the steps I followed for setting up a comments system running on my own site

### Why I host my own comments, and why you should want to

This site is a static website, meaning that each page you click to exists as an html file on the server.
A static site is much easier to maintain and likely more secure than a dynamic site, where the pages are generated on the fly with software running on the server.
One problem of static sites is that it is difficult to deal with content like comments.
Comments are inherently dynamic and interactive: an existing page must take input from a user, this data must be sent to the server and somehow stored there, and then when the site is visited again it must display this new content.
It is difficult, probably impossible, to do this in plain html.
Usually, static sites like blogs deal with this by relying on plugins provided by third parties, like [disqus](https://disqus.com/) or facebook comments.
These are popular because they have a free tier.
This removes all the hassle of hosting and managing comments; inserting a comment thread is achieved by inserting an html snippet to the page.
The data in the comments is stored on the servers of the third party, and the blog owner manages them via a dashboard provided by the third party.

While convenient, this solution comes at the price of the site owner's freedom and that of the site visitors.
In order to comment, users must have a facebook or disqus account.
The site owner is at the mercy of inflexible and opaque user license agreements.
This could mean that unwanted adds will be displayed on the page.
The site could also be banned from the free tier with no explanation, and then the site owner will be coerced into the subscription model.

This happened to me on this site with disqus, which was my first comment system.
They offer a free tier if they can show ads on the site, provided the site follows their guidelines.
The guidelines basically dictate violent or lewd content is a no go.
I thought: No problem, this site has nothing edgy on it (except if you consider the article on text editors controversial).
After a few weeks, out of the blue I received an e-mail from disqus that my site violates their guidelines, and that if I want to continue to use their services I must upgrade to one of the paid plans, starting from $11/month.
Given that this site gets almost no traffic, $11 every month is quite steep.
The most frustrating part was that I was given no explanation regarding my ban, for example what the infringing content might be.
Customer service basically repeated the same thing as what I had received in the e-mail.
So I can only guess as to why they banned me.
Is it the .xyz domain which is often sketchy?
Is it the fact that on my c.v. the word *cum* appears in the text from the Latin *Cum Laude* (with distinction)?
Or is it simply that disqus measured that my site gets limited traffic, and they shouldn't even bother showing ads on my pages.
I suppose I will never know.
But this for me again highlighted the limitations of being reliant on some third party platform or service: in return for convenience you relinquish a lot of power to them.

I tried facebook comments for a while, but the plug-in doesn't seem well maintained or even advertised by facebook.
Many browsers block it due to facebook trackers and users must log into their facebook accounts to be able to comment under their own name.

I knew that if I wanted to do comments my way, I'd have to host them myself.
But I wanted it to work in a similar way as the other comment systems, basically as a plug-in to a static site.
Turns out there are not so many solutions for this niche, which is probably why disqus can charge such ridiculous fees.
You either create an entirely dynamic blog with Django or Flask, or you just don't have comments.
Until I read about [cusdis](https://cusdis.com/) through the [Jackson Kelley's Console newsletter](https://console.substack.com/).

Cusdis, with its tongue-in-cheek name, is a very cool new little project created by Github user djyde that precisely fills the niche I was looking for.
It's free and open source, and basically allows you to run your own little comments system and dashboard.
My idea was to install it on the same server as this site, and replace the terrible facebook comments system.
Unfortunately the documentation is very minimal, so I thought I would create this blogpost.

### Installation and configuration with nginx

My server is already running multiple web services, including this static site.
Hence I'm using Nginx to route different subdomains to the right ports.
If your server only needs to run cusdis, you may not have to deal with all of these issues.

* Ensure you have `docker` and `docker-compose` installed on your server. The command to do this will depend on the operating system you have running. For my Debian box this is `apt-get`.
* For convenience, with your domain registrar, register a subdomain for the cusdis dashboard. So if you have a domain `website.com`, register something like `cusdis.website.com`.
* Create a file `docker-compose.yaml` with te following content (fill in things):
```yaml
version: "3.9"
services:
  cusdis:
    image: "djyde/cusdis"
    ports:
      - "3000:3000"
    environment:
      - USERNAME=<your username for dashboard site here>
      - PASSWORD=<your password for dashboard site here>
      - JWT_SECRET=<jwt secret for enabling web hooks>
      - NEXTAUTH_URL=<url to cusdis dashboard, including http(s)>
      - DB_TYPE=pgsql
      - DB_URL=postgresql://cusdis:<postgress password>@pgsql:5432/cusdis
  pgsql:
    image: "postgres:13"
    volumes:
      - "./data:/var/lib/postgresql/data"
    environment:
      - POSTGRES_USER=cusdis
      - POSTGRES_DB=cusdis
      - POSTGRES_PASSWORD=<postgress password>
```

  You basically have to create 3 very strong passwords: one to access the dashboard, one to access the postgres database, and one to enable web hooks.
  Of course modify ports if port 3000 is already taken.

* Pull the docker images of cusdis and postgresql and create the containers with `docker-compose up -d`.
  * In case you want to update the images I recommend:

```bash
$ docker-compose pull
$ docker-compose up --force-recreate --build -d
$ docker image prune -f
```

* Now add the following block to your `/etc/nginx/sites-enabled/<config filename>`:

```
server {
  server_name <subdomain for dashboard>;

  access_log /var/log/nginx/<subdomain>.log proxy;

  location / {
      proxy_pass       http://localhost:3000;
      proxy_set_header Host      $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      if ($uri = '/js/iframe.umd.js') {
            add_header Access-Control-Allow-Origin '<URL to sites that need access>';
      }
  }
}
```

  The strange `add_header` block was a solution to an annoying CORS issues proposed by Github user `nauicha`, see [this thread](https://github.com/djyde/cusdis/issues/135).
  The point is that the service could run on the server, but the blog that needs to access the comments seems to be hosted on a different domain according to the browser (even though they may be on the same physical server).
  This made it so that no comments showed up on any of the pages.
  We need to explicitly tell NGINX that the blog can make requests to cusdis.
  If you want any site to be able to access the cusdis service, you should add `'*'`.

* Rerun certbot and restart or reload the nginx service (I'm assuming you are running some Linux version with systemd)

```
$ certbot renew
$ systemctl reload nginx
```

* It should now be possible to visit the domain you specified and access the dashboard. Log in with the credentials you specified in the docker-compose file.

* Now add the comment widget to the pages on your site by adding the following to the HTML (must be copied from the dashboard):

```html
<div id="cusdis_thread"
  data-host="<URL to the subdomain where cusdis is hosted>"
  data-app-id="<app-id -- see your dashboard>"
  data-page-id="<id of the page on which it is embedded>"
  data-page-url="<URL of the page on which it is embedded>"
  data-page-title="<title of the page on which it is embedded>"
></div>
<script async defer src="<URL to the subdomain where cusdis is hosted>/js/cusdis.es.js"></script>
```

  If you use a static site generator, you can use macros to fill in `data-page-id`, `data-page-url` and `data-page-title` (check the source code of this site for example).

That's it, now there should be a little comment section on your pages that connects to your self-hosted comment system!

### Why you may not want to host your own comments

Managing your own comment system also has drawbacks of course.
It runs on infrastructure you control and so you are responsible for ensuring it has enough resources like memory and disk space.
You're also responsible for security, and running additional software on your server potentially opens up additional attack vectors.
Cusdis in Docker, as with most node projects, is pretty bloated; at the time of writing just the cusdis image is 2.6 GB in size!
If you use only a minimal VPS it can definitely strain the available resources.
In addition, cusdis occasionally crashes on me for no reason I've been able to determine, but I'm sure stability will improve over time.
There's also really no one to complain to when things don't work.
The CORS issue I faced was open for multiple months before someone found a reasonable solution.
That's the nature of open source.
Finally, As the project says on its README, there is no spam filtering either, so your site could become a target for bots (not yet a huge issue).

### Conclusion

This post explained how to set up cusdis behind nginx to host your own comments system on a static site you may be hosting yourself.
It's a really cool project, and I want to thank Github user djyde for creating it.
Hope you found this post useful.
