Title: Search and install multiple packages with pacman
Date: 2021-09-21 13:40
Category: Arch Linux
Tags: software, Linux, computer
Summary: Some shell tricks to search and install multiple packages at once

Arch Linux takes its bottom up approach very seriously and the system you start with has basically nothing but the bare essentials installed.
I got a bit tired of seeing glitchy text on the web because my system didn't have have them, so since I have a pretty powerful computer with a ton of storage I thought I would install all the available fonts in the repos.
So I went to the shell and did

```bash
$ pacman -Ss ttf font
```

and got output that looked something like

```
extra/gnu-free-fonts 20120503-8
    A free family of scalable outline fonts
extra/noto-fonts 20201226-2
    Google Noto TTF fonts
extra/noto-fonts-extra 20201226-2
    Google Noto TTF fonts - additional variants
extra/sdl2_ttf 2.0.15-2
    A library that allows you to use TrueType fonts in your SDL applications (Version 2)
extra/ttf-bitstream-vera 1.10-14
    Bitstream Vera fonts.
extra/ttf-caladea 20200113-3
    A serif font family metric-compatible with Cambria font family
...
```

It was a pretty long list of packages, all with pretty long names, and I really couldn't be bothered typing all of those out.
So I started digging to figure out how I could use the output from `pacman -Ss` to `pacman -S`.
I came up with the following (probably less than optimal) solution:

```bash
xargs -a <(pacman -Ss ttf font | grep "^[a-zA-Z0-9]" | sed 's/^.\+\///; s/\ .*$//' | grep -v "ttf-nerd-fonts-symbols-mono") sudo pacman -S
```

It probably took me longer to figure out how to do this and to then write this blog post about it, but anyway, let's disect it:

1. Inside the parentheses we pipe the output from `pacman -Ss` to `grep` where we only want to get the lines that start with a letter and number. The regular expression `^[a-zA-Z0-9]` will achieve this. The indented lines describe the package and are useless; they are filtered out.
2. We pipe those lines to `sed`, where we remove everything before the forward slash with the expression `s/^.\+\///`, where we look for the start of the line (`^`), then any kind of characters (`.`) a number of times (`\+`), then a slash `\/` and we replace with nothing. We also remove everything after the space (`\ `) until the end of the line (`$`).
3. (Optional) I piped this again to grep because this package conflicted with another package. With `-v`, I let everything pass except the matches
4. This is directed to `xargs` with the `-a` flag which passes the list of packages to `pacman`. The reason we can't just pipe the output of the second grep to `xargs` is because `pacman` requires yes/no confirmation, which is not possible in that mode. A helpful stack exchange thread on this can be found [here](https://stackoverflow.com/questions/30044927/xargs-exec-command-with-prompt).

Hopefully this could be helpful if you want to do something similar.
