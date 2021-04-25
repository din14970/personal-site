Title: The natural editor progression of a contrarian
Date: 2021-04-24 13:40
Category: fluff
Tags: software, text editing
Summary: The story of my changing editor preferences


### The beginning
I learned the basics of python over the summer of 2015 on my personal Mac.
I thought it would be a good investment of time going into a Ph.D. and this turned out to be a good bet.
The book I followed was [Learning Python the Hard Way](https://learncodethehardway.org/python/) by Zed Shaw.
At that time, it was still a free online book about python 2.
The author recommended to learn python 2 since "python 3 would never take off" and to use any plain old text-editor, not an IDE.
So my coding journey started with **TextMate**.

When I started the Ph.D. I got a work laptop running Windows, so I switched to **Notepad++**.
It had syntax highlighting, it was simple, it didn't get into my way, I was happy.
Then I discovered Jupyter notebooks, and since I was mostly doing experimental data analysis and plot creation this was where the bulk of my code was written.
For four years, I was happy with these tools at my disposal.
It is remarkable how people can be perfectly happy with a suboptimal way of working, not even considering that there are better ways of doing things.
Once we are used to a certain workflow, it can be difficult to change it; this requires effort to learn and adapt, and some time of being less productive.

### The transition stage
A number of events made me reconsider my ways and explore alternatives.
A friend introduced me to Linux, raspberry-pi, the command line, and the open source community.
Coming from Windows and only knowing a bit of python, this was a huge culture shock for me.
But his introduction led me down a rabbit hole that ultimately gave me a better overview of computing and software history.
I feel like this is because when you learn about Linux and the command line, you strip everything down to the fundamentals.
After my Ph.D., during my Post-doc, I delved deeper into software development and computational topics. 
I had traded in my Windows PC and was back with my Mac, so I was forced to reconsider my workflow.
Luckily my new knowledge of Linux allowed me to make better use of my Mac, given that OSX derives from BSD and is "Unix-like".
In fact, I became frustrated with the limited flexibility of OSX and the various incompatibilities with Linux.
While I still use my Mac, this will hopefully be the last one I ever own.

Going back to TextMate wasn't going to do it.
Another friend introduced me to [**Atom**](https://atom.io/) which looked really practical with all the extensions.
This editor had lots of features which I didn't know I wanted until I tried it, like a file browser and terminal directly in the editor.
I also discovered [hydrogen](https://atom.io/packages/hydrogen) which could run code in-line like a Jupyter notebook.
In the end I never used it because it was quite buggy when using it with various virtual environments.
But I configured Atom exactly to my liking and felt like I had made a serious upgrade to my workflow.

However, the future of Atom didn't look very bright.
Github, the maintainer of Atom, was acquired by Microsoft which was strongly promoting VSCode.
VSCode in many ways is similar to Atom; it is an editor based on electron and has a similar plug-in system.
There is no reason for Microsoft to keep maintaining Atom, so it is at a high risk of becoming abandonware.
The popularity of **VSCode** was exploding exponentially, and with users came developers and plug-ins.

So I checked it out.
I hated it.
Instead of VSCode, I tried **VSCodium**, the community compiled version.
Included in VSCode is mostly open source but does get bundled with shady proprietary telemetry code (i.e. Microsoft spying on you).
VSCodium is compiled using only the open source part.
As one might expect, it just doesn't work as well as the Microsoft VSCode binaries, similar to how Chromium is not fully compatible with Chrome.
Many of the plug-ins I wanted just didn't work, and the program would randomly crash.

But even the proprietary VSCode gave me problems.
The "tags" system for code navigation was excruciatingly slow.
The settings menus were ugly and incomprehensible.
Everything was just a bit "off" for me, and I didn't have the "friendly" feeling as I did with Atom.
The final nail in the coffin was the fact that the plug-in space was called *marketplace*.
I did not want to become dependent on VSCode paying or subscription based extensions.
To this day, I still don't understand why people enjoy VSCode so much.

VSCode was out for me, but I was still looking for an alternative to Atom.
I considered Spider and PyCharm but ended up not investing time in them.
Spider took forever to open on my laptop and was just a bit clunky.
PyCharm is also a fan-favorite of python developers, but the closed-source and freemium nature made it quite off-putting for me.
My biggest gripe with these editors was their exclusive python focus; I want one universal editor for all my text editing and coding needs.

### The enlightened stage
For me it was time to go all the way to the fundamentals and invest time to learn **Vim**.
I'd seen some crazy YouTube videos on the power of Vim and decided to buckle down to learn it.
The features that attracted me to Vim were:

* the promise of speed because you no longer need the mouse. In the end, I still use the mouse occasionally as it's more convenient for scrolling, so I'm not sure whether I really save much time using Vim.
* *hackability*; you can configure the editor entirely in plaintext and there are lots of free plugins. There is no limit to configurability due to buttons hidden away in a user interface.
* available everywhere that runs Linux. Since I occasionally need access to a text file on a server or inside a docker container through a minimal command line interface, knowing Vim is really helpful.
* configurable to work for any language. This was a big one for me, as I wanted a text editor that could handle both LaTeX and Python, and possibly other languages. VSCode didn't really have good support for LaTeX.
* it offered a challenge to learn something I'd heard was hard.

I took [this](https://www.udemy.com/course/vim-commands-cheat-sheet/) Udemy course and then just went in to force myself to use it.
I briefly used **Vim 8**, but ultimately decided **Neovim** to be the more future proof option.
More and more plug-ins are written in Lua and no longer support Vim.
Currently I've been using Neovim inside ITerm2 exclusively for about a year and haven't looked back.
My configuration is yet what it needs to be, and I would like more time to really finetune this, but it does what I need it for.
With Vim there's always something new to learn.
It's a steep learning curve but it pays of in the end.
I highly recommend looking at the YouTube videos of [ThePrimeagen](https://www.youtube.com/channel/UC8ENHE5xdFSwx71u3fDH5Xw), [TJ DeVries](https://www.youtube.com/channel/UCd3dNckv1Za2coSaHGHl5aA) and the [blog of jdhao](https://jdhao.github.io/) for inspiration.

### What is next
At the moment I'm content with neovim, the plug-ins, ease of use and flexibility.
But it looks like the final stage of text-editing enlightenment is always **Emacs**.
I've heard some very cool things about [org-mode](https://orgmode.org/) and [spacemacs](https://www.spacemacs.org/) for example, and Emacs lisp is apparently a much more friendly configuration language than vimscript.
Then again, with Neovim, Lua might be just as good.
When you reach the Emacs stage, you basically replace your entire operating system with your text editor; when you spend the majority of your time in text, this might just be worth it.
