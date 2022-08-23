Title: Restoring files that were never committed with git
Date: 2022-08-23 13:40
Category: DevOps
Tags: software, git, restore
Summary: Going back to a history that never existed

Recently I started a new project that I wanted to manage with git version control.
I made the cardinal mistake of doing a lot of work before making a first commit.
Just when I was about to make my first commit, disaster struck: I accidentally deleted everything with `git rm`.
This command is in many ways similar to the `rm` utility: the files are deleted from the file system and are unrecoverable from "a recycling bin".

How did such a thing happen?
Normally I use git on the command line, but in this instance I was using KDE with Dolphin as a file manager plus a git extension.
Of course I miss clicked in the menu and chose an option that corresponded to `git rm`.
And just like that, my work was erased.

Obviously if the files were committed to history, there would be no issue whatsoever.
Just check out an earlier commit.
Typically you can use some variation of `git restore`, which is also what all StackExchange answers I found told me to do.
But I found this doesn't work when `HEAD` doesn't yet point to anything.

However, I was still able to restore some of my files.
I had performed `git init` before I started working, so there was still a `.git` folder in the directory.
I had never really bothered with the internals of this folder, but it seemed like it wasn't empty, and there were some things in the `objects` subfolder.
Maybe, git kept some cache of the working directory in there?

The files in `objects` were not directly interpretable with `cat`, so probably they represent some binary encoding or compressed representation of original files.
It was also not possible to figure out what each object was just from the filename.
However, I could inspect the objects `git` remembered using 

```
$ git fsck
```

This printed out a list of hashes that corresponded to objects.
I went through this list one by one using the following command

```
$ git show <HASH>
```

Amazingly some of these objects corresponded to the content of my files!
I could then manually restore these files with 

```
$ git show <HASH> >> <filename>
```

There is a caveat here: these objects were only in the `objects folder` because at some point I had done `git add` before I did `git rm`, which made git aware the file existed.
So you will only be able to restore objects that were `staged` at some point using this method.
Also, `git prune` will delete all these references if they were there, so beware!
Finally, it's pretty unlikely this will occur to you if you use the command line version of git -- `git rm` will not even work on staged files.
But apparently on the KDE Dolphin git plugin it does.

