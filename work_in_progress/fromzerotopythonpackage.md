Title: From 0 to open source (scientific) python project
Date: 2021-02-06 17:53
Category: Python
Tags: github, packaging, CI/CD, science, testing, documentation
Summary: How to go from spaghetti code to a high quality open source Python project

### Motivation
In many ways, coding has never been easier.
The practice used to be a specialized craft for a select club of eccentrics, but tooling has advanced to a point that it has become accessible to a much wider community of developers.
Widespread adoption of "easy" programming languages with friendly syntax like Python and Julia, the thousands of libraries in those ecosystems, and the endless free online resources to learn basic coding have democratized programming to a great extent.
The meteoric rise of the data science profession can arguably be attributed to the emergence of the scientific python stack (scipy, numpy, pandas, matplotlib, ...) and Jupyter notebooks. 

A downside to the democratization of programming is that the number of beginners greatly outnumber the veterans, which has a direct impact on project code quality and an indirect impact on the available educational resources.
A [stackoverflow survey](https://insights.stackoverflow.com/survey/2020#developer-profile-years-coding-professionally) indicates that the vast majority of professional coders had less than five years of experience.
How representative the data from respondents is for the industry overall is debatable - veterans might not bother to fill out stackoverflow surveys - but it can't be denied that there are a lot of young and relatively inexperienced people contributing code to the universe.
Whereas programmers who were around in the early days of computing have an intricate understanding of the machine and know how to write efficient programs using minimal resources, young developers without this expertise are more prone to write inefficient bloated crap.
Educational resources like bootcamps and tutorials tend to cater to this large army of newbies, but these rarely delve deeply into the subject matter fundamentals.
Leveling up past the basics is hard because there are relatively limited resources for intermediate to advanced programmers.

For researchers in the physical sciences as well as data scientists (who often come in from the physical sciences in academia), "coding" often only serves the purpose of extracting meaning from data in an interactive and flexible way.
They might have a lot of experience with different tools and high level frameworks like TensorFlow or PyTorch, but they often do not have the background in computing or programming best practices to develop full fledged applications.
Code tends to remain rough, non-performant, non-reusable and often resides entirely in Jupyter notebooks.
This is a shame, since it results in a lot of fragmentation and duplicated effort in niche fields.
Placing higher demands on code quality and thinking about maintainability from the start is beneficial in the long run, both for the creator and potential users.

I myself am guilty of writing a lot of crappy spaghetti code, under the moto "working code is good code".
Part of the reason is that when you are mainly self-taught, you don't have the roadmap to the knowledge you lack but may need.
The result is code that resembles stackoverflow answers duct-taped together.
The project structure is a mess and you don't adhere to any tried and true good practices.
Because best practices are often so hotly debated, there is rarely any official education and resources on these topics, and everyone "just wings it".

This article is not about how you can write high quality python code; I think no one can teach you this, you can only learn from experience and by seeing lots of examples.
Instead, this article is about all the infrastructure and tooling you should be aware of when making a python project in 2021.
It is aimed at people who may be following a similar path as myself: (data) scientists who can throw something together in python and a Jupyter notebook, but who don't have an extensive CS background or experience with modern DevOps tooling.
I aim to answer questions like:

* How do you get past the stage where all your code exists in loose Jupyter notebooks or scripts and make something that others can use?
* What are best practices on project layout?
* How do you ensure your code works and prove this to potential users so they are confident in using your project?
* How should you distribute your code?

While I am definitely not an expert on all the tools and techniques in this post, I thought I would make the extensive overview that I wished I had when I was trying to improve my own python game.

### My assumptions about you
I will assume you already know python.
I assume you are aware and comfortable with the scientific python stack and Jupyter notebooks.
Beyond that, I will assume you have very little deep knowledge about computers.

### Get comfortable with Unix and bash
Python claims to be platform independent and many scientists coming from academia are likely using it on Windows.
With Jupyter notebooks running in the browser, it may be a while until you run into the quirks of Windows.
Have you ever wondered why developers often have macs or run Linux?
There are many reasons, but the bottom line is that OSX and Linux are both based on the Unix operating system, whereas Windows is based on DOS which is a completely unrelated system.
A lot of small differences that on the surface seem like minor inconveniences can turn into major headaches down the line when you only account for the way Windows does things.
As a small example, file paths in Windows use the \ backslash, whereas Unix based operating systems use the / forward slash.
The backslash in Python can in some contexts be interpreted as a special character, and you should always be careful when using simple strings as file paths as this can yield annoying bugs on different platforms; always using [Pathlib](https://docs.python.org/3/library/pathlib.html) or [os.path](https://docs.python.org/3/library/os.path.html) for working with paths.

So why don't we all just work with Windows if most people are using this as their daily driver?
Well, the large majority of servers and supercomputers are running Linux, and since most development is focused around web technology and remote services developers like to develop in a similar environment as where their code will be deployed.
In addition, as a developer you tend to spend quite a bit of time in a terminal/command line interface.
And let's face it: windows command line is simply garbage in comparison to the bash or zsh shells that run on Unix operating systems and have access to BSD and GNU utilities.
Once you get a little bit more serious about developing you will discover all the little inconveniences of Windows, and may flirt with installing Ubuntu.
Or you might be lazy and buy a Mac.

But even if you never encounter issues with Windows and you are not developing web applications, you will still need to learn the basics of Linux and the bash shell: you will likely interact with modern technologies like Docker containers and CI/CD services (see later) at some point, and these are also running Linux.

Here are some links to some nice articles to help you get started:
* <https://towardsdatascience.com/basics-of-bash-for-beginners-92e53a4c117a>
* <https://guide.bash.academy/>

Bash is pretty much a scripting language in and of itself that can do some things much more effectively than python.
If you need to do a bunch of operations on files and directories, you might consider writing a Bash script instead of a python program.
But to support your python development journey, you just need the basics of Bash.

### Git and Github
If you are anything like me a few years ago, you are vaguely aware of git and Github, but it all seems rather complicated and you haven't really bothered dealing with them.
Let me tell you that this is a mistake - try to incorporate git and Github into your workflow as soon as possible.
What are git and Github?

[Git](https://git-scm.com/) is an advanced version control system that you mainly interact with through the command line, and it is the de-facto standard for version control in (open source) software.
Do you often find yourself in the situation where you create and store multiple versions of files?
If you are the only one working on those files this is manageable, but the problem becomes exponentially harder when you try to collaborate on the same documents with multiple people.
It is these issues that git aims to deal with, particularly when applied to source code.

I can not do full justice to the power of git in this short article.
I have created an (embarrassingly low quality) video series about the tool for my colleagues, which you can check out on [YouTube]().
The bare bones of git you need to know:


### Project structure
Ok, here we are getting to the meat.
If you are building a pure python package, chances are

### Distributing your package


### Unit testing and code coverage


### Documentation and examples


### Code formatting


### CI/CD pipelines


### Getting people to cite your package


### Going further


### Summary
