Title: How this site was built
Date: 2021-01-03 13:40
Category: Website
Tags: pelican, css, html, bootstrap
Summary: Here I go over the general process to create and deploy this site

### Motivation
I have been getting a bit frustrated recently with the cookie-cutter online profiles and services we must subscribe to in order to stay relevant: LinkedIn, ResearchGate, ORCID, Facebook, Twitter, Instagram,...
The scope for profile customization is very limited and there are always concerns about what happens to your data when handed over to big tech.
Therefore, I was long toying with the idea of creating a personal online presence that I can customize *ad infinitum* and where I can post whatever I want.
Somewhat recently I started renting a VPS on [Vultr](https://www.vultr.com/), so I thought I would a blog/portfolio/personal page there.
I've had WordPress blogs before, but this time I wanted to start from scratch.
Before this project, I didn't really have any experience creating websites but it's something I wanted to know the basics of; this is best done by starting with the basics.
Additionally, I figured some web-design experience might be a useful skill to have.

However, I also didn't want to go too deep.
These days even the most simple looking sites have lots of tech behind them, such as JavaScript in the front-end to serve up dynamic content for the user, and php, python or again JavaScript to talk to databases and other services in the back-end.
Web development really is a career path on its own, with developers generally specializing in some kind of framework like React, Angular or Django to create their projects.
It is impossible to get an overview of, let alone learn, all the tools available to web devs these days.

To keep it as simple and secure as possible, I wanted a static site.
A static site is basically where each page exists as an html file on the server, as opposed to a dynamic site which generates the pages to serve to the user on the fly.
For a simple personal website with a minimal blog, this should be fine.
But writing out each html file manually would be extremely tedious, especially if there are repeating elements on each page like a navigation bar.
If you want to change the layout of your site, you have to edit all the files.

Enter static site generators.
Your site source code consists of html templates and content written in easy markup syntax like markdown.
You then run the generator, which "compiles" the individual html files for you, which you then upload to the server.
No messing around with databases and credentials, and thanks to the minimal code you need you can create a personal website rather quickly.

After a bit of research I stumbled upon [Jekyll](https://jekyllrb.com/) and [Pelican](https://blog.getpelican.com/).
Jekyll seems to be the most popular static site generator, but it uses Ruby which I was a bit reluctant to learn.
Pelican is a less popular option, but it is built with python, which I know well.
It also uses [Jinja](https://jinja2docs.readthedocs.io/en/stable/) for the html templates, and since I had looked into Flask before I was somewhat familiar with this syntax.
This was easier for me to dive into, so I went with this option to build this site.
While the default syntax for creating articles seems to be RST, I wanted to write markdown, which is also supported.

I also wanted the site to work well on all screen sizes, and I read [Bootstrap](https://getbootstrap.com/) is often used for this purpose.
So part of the challenge was integrating Bootstrap into the templates.
I really only use the bootstrap grid system.

### Installation

I already have the [Anaconda](https://www.anaconda.com/products/individual) python distribution on my system and created a virtual environment in which I installed the necessary dependencies.
For this I followed the [pelican quickstart documentation](https://docs.getpelican.com/en/latest/quickstart.html).

```Bash
$ conda create -n devel pip
$ conda activate devel
$ pip install "pelican[markdown]"
```

I also wanted to be able to write mathematical equations like $\sqrt{x}$, so I also installed the [render-math plugin](https://github.com/pelican-plugins/render-math).

```bash
$ pip install pelican-render-math
```

Note that on Mac OS, bash can get confused with pip and might try to use the system pip depending on your `PATH` variable.
Check this with `which pip` and if it is the incorrect one try using `pip3` or `python3 -m pip` instead of pip.
You can also change your `PATH` or create aliases in your `.bashrc` file.

### Initial setup

Going from the quickstart guide, I created a directory and a dummy project

```bash
$ cd path/to/folder
$ mkdir project_name
$ cd project_name
$ pelican-quickstart
```

Then I just followed the prompts.
The domain name I filled in for my URL is `https://nielscautaerts.xyz`.
Then I created this article as a test.
In addition, I wanted to have 3-4 static pages: a welcome page with a summary about myself, a contact page with links to my socials, a resume page with a full record of my academic acivities, and possibly a projects page that would serve as a kind of portfolio. 
I decided to skip the portfolio for now and focus on the rest.

I structured my `content` folder as follows:

* **blog**
    * This-article.md
* **images**
    * miscellaneous images
* **pages**
    * contact.md
    * home.md
    * resume.md

I wanted the landing page to be a static welcome page, not a list of blog posts. This is not default behavior in Pelican. 

### Serving and developing locally

To monitor the site progress, I set `RELATIVE_URLS = True` in `pelicanconf.py`. To create the site for the first time from the source code, I run:

```bash
$ pelican content
```

This generates the site in the `output/` directory.
You can just open the html pages in this folder with a browser by double-clicking on them.

I wanted all pages to update automatically every time I made a change, so I could simply refresh my browser to view them.
To do this I opened a new terminal window and run:

```bash
$ pelican -l -p 9000 -r
```

The `-l` flag is short for `--listen` and will serve up the site by default on `http://localhost:8000/`.
I changed the port with `-p` to 9000.
The `-r` flag regenerates the site every time I make a change to the source code.

Sometimes the browser would still show me old pages because it is keeping some information in cache.
To hard-refresh the entire page, on Mac and Firefox I could use `Cmd + Shift + r`.

### Changing themes and styling

The default Pelican theme is extremely ugly and cluttered, so I decided to just start from scratch.
This would give me a chance to play with the Jinja templates, the CSS, work Bootstrap in there, and make it just to my liking.
Ok, I didn't truly start from scratch, I started from [the simple theme](https://github.com/getpelican/pelican/tree/master/pelican/themes/simple/templates) included in the Pelican repository, and gradually modified those.
I created a folder `layout-theme` in the project root folder which is structured as follows:

* **static**
    * **css**
        * code_styles.css
        * style.css
* **templates**
    * *article.html* - the template for a single blogpost page
    * *base.html* - the template for all pages
    * *categories.html* - the template for a page containing a list of links to all categories
    * *category.html* - the template for a page containing all posts in a category
    * *index.html* - the template for the page containing all posts
    * *page.html* - the template for static pages
    * *pagination.html* - the template for the little pagination links at the bottom of post list pages
    * *tag.html* - the template for a page containing all posts with a tag
    * *tags.html* - the template for a page containing a list of links to all tags

The `style.css` is a manually created file in which I added my custom styling to page elements.
The `code_styles.css` is an additional css file generated with [`Pygments`](https://pygments.org/) to automatically style syntax in code blocks in the articles and pages, basically anything between \` and \`\`\`.
When creating a code block in a markdown, Pelican will put that into a div or table with the class `highlight` in the rendered HTML, so elements inside such a block can be styled by the css file.
Under the hood it is using [CodeHilite](https://python-markdown.github.io/extensions/code_hilite/#syntax) for this, a [Python Markdown](https://python-markdown.github.io/) extension.
I generated the css file with:

```bash
$ pygmentize -S default -f html -a .highlight > layout-theme/static/css/code_styles.css
```

It is important that the `-a` flag is `.highlight`; this is the class attached to code blocks by Pelican.
If you choose the default as explained in step 2 of the CodeHilite documentation, it won't work.
Here I used the default color scheme, but [there are many more to try](https://pygments.org/demo/#try).
I quite liked the dark color schemes, but unfortunately those don't seem to work well with Bash or Shell scripts.

By default, pelican also generates a page that lists the post authors and one that lists the posts by each author.
As I am the only author here, I disabled those with `AUTHOR_SAVE_AS = ""` in the `pelicanconf.py` file.

I spent quite a bit of time on creating the navigation bar in `base.html`.
To add bootstrap to the site I added in the header:

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
```

Probably I could do it quicker now, but it was my first try with bootstrap.
I specifically wanted a menu bar where the options would collapse to a button on small screens.
To this end I looked up some examples [here](https://www.w3schools.com/bootstrap4/bootstrap_navbar.asp), and mixed, matched and modified accordingly.
Getting the button to work was especially tedious.
What tripped me up is how bootstrap sometimes seems to override custom CSS.
Especially the `navbar-dark` class I am using didn't seem to work well with custom colors and fonts; it just seems to ignore it.
Currently, in my `static.css` file, I just make heavy use of constructs like:

```CSS
.classname {
    color: #FF00FF !important;
}
```

This seems to do the trick of overriding the Bootstrap styling.
Probably this is not really best practice, but it works for now.

I'm not a big fan of copyright, so in the footer I added some copyleft information.
The copyleft symbol is made by rotating the copyright symbol 180&#176; with CSS.

It was a bit more smooth sailing on the other templates from there.
Obviously you can go check the source code on [Github](https://github.com/din14970/personal-site), it's difficult to go over all the details.

For the static pages that I wanted (home, resume and contact), I felt like I couldn't really do what I wanted with simple Markdown.
So I wrote the source code entirely in HTML, since this is also accepted in Markdown files.
Since I only need to update those occasionally and not write all that much there, this should be fine.
This way I could also use the bootstrap classes in the file, and add things like a picture of which the position changes depending on the screen size.

### Custom settings and site navigation
To ensure these pages would be rendered and correctly added to the navbar as programmed in the `base.html` page, I added the following to `pelicanconf.py`:

```python
MENUITEMS = (("Home", "/"),
             ("Resume", "/cv.html"),
             ("Blog", "/blog_archive.html"),
             ("Contact", "/contact.html"),
             )
```

Then at the top of each markdown source file I matched these entries with the metadata:

```markdown
Title: Resume
Save_as: cv.html
```

By default in Pelican, the index page is an overview of all the blog posts.
To ensure that the page you land on first is the static home page, the `home.md` should have the metadata:

```markdown
Title: Home
Save_as: index.html
```

This can be a bit confusing, because the `index.html` template in the `layout-theme/templates` folder is not what will be used to create the index for the final site.
The `index.html` template will instead be used to create the `blog_archive.html` page, as I define it above.
To tell Pelican to do this, I set `INDEX_SAVE_AS = "blog_archive.html"` in `pelicanconf.py`.

A couple of additional miscellaneous settings:

* To enable the `render_math` I added `PLUGINS = ["pelican.plugins.render_math"]`
* I'm a big fan of the Japanese style date format, which I set with `DEFAULT_DATE_FORMAT = "%Y-%m-%d"`
* I decided to have 5 posts on each "listing" page, which I set with `DEFAULT_PAGINATION = 5`

There are probably some other settings in the `pelicanconf.py` file which actually aren't doing anything because I messed with the templates so much.
Experimenting with deleting the clutter is work for a later stage.

### Deploying the site

That's pretty much it for content, layout and settings.
There's still some things I'm not completely happy with, like I would like some padding on the code blocks, but haven't found a good way to do it.

To get the site on the server, use the other config file to regenerate the site:

```bash
$ pelican content -s publishconf.py
```
The site will no longer work locally because all the links should have been replaced with absolute paths.
The settings from the `pelicanconf` file should be loaded by default. I haven't changed any settings here, but one might add google analytics and [DISQUS](https://disqus.com/) information here.

Now all you need to do is somehow get the content of the `output` folder in the right place.
For a first try I just used [FileZilla](https://filezilla-project.org/) to drag and drop everything into `/var/www/html/sitefolder`.
On this server I already had [NGINX](https://www.nginx.com/) configured so this worked out of the box and I could access my site.

After updating this article, I also tried `rsync`. There should be also some automation tools which are described in [the documentation](https://docs.getpelican.com/en/latest/publish.html).

### Summary

In this article I went over how I created this site with Pelican and Bootstrap.
It mainly serves to keep a record for myself, but maybe someone else might also find it useful as a complement to the Pelican documentation.
