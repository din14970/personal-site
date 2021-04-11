Title: Showing changes (diffs) with LaTeX and git
Date: 2021-04-07 13:40
Category: LaTeX
Tags: git, LaTeX, science, papers, writing
Summary: A simple reason why you need to write your papers using LaTeX and git

I used to write my scientific papers in MS Word.
There are many conveniences to Word: what you see is what you get.
Content is formatted by clicking the right options, and the final product is immediately visible.
Adding non-text content is pretty convenient: you drag images in from the file browser, and you can rather easily insert decently formated equations and references.
While I'm generally not a fan of Microsoft products, I must admit Word is a pretty good solution for many use cases.

However for scientific publications, there is a real advantage to using the powerful combination of LaTeX and git.
Whereas Word documents are opaque binary files that contain all the formating, images, and text inside, LaTeX source files are just plain text that can be edited by any text editor.
This means that LaTeX in most like source code, whereas a Word document is more like a compiled program.
With source code and plain text files, we can use utilities like `diff` to easily check differences between documents, and we can easily check them into version control software like git to keep track of incremental changes.
This doesn't work for Word documents -- each change must be checked into source control as a new document, and differences between versions can not be easily visualized (unless you use the built-in *compare documents* feature in MS Word).
Since formatting is just encoded in text in LaTeX source files, all of it is easily managed with version control.

Why would you care about version control for scientific publications?
Because scientific papers tend to go through many, many, many iterations.
And because it's a document that many authors collaborate on and simultaneously review, keeping an overview of the state of the document can be an absolute nightmare.
How often has it happened that one author submits one piece of the paper, another has changed a part, while yet another has reviewed an older version of this part?
If everyone used git and LaTeX, none of this would be an issue.
People can just pull in the latest changes from master and review or make additions from there.
One thing to keep in mind: `diff` and `git diff` verify changes on a  *line-by-line* basis.
So when writing LaTeX it is a good idea to write each sentence on a new line, so that changes are dealt with on a sentence by sentence basis.

The main problem you will face with this scheme is that your colleagues will likely not switch to LaTeX or git.
They will still want to review the document in a PDF or Word format.
So you will again end up with different versions and having to copy changes from PDF files into your source code.
But there are still two reasons that makes LaTeX+git worth it: `latexdiff` and branching.

Let's look at `latexdiff`.
Let's say you have submitted your publication to a journal and it comes back with major revisions.
For the revision you have changed a lot of things on the document.
On the resubmission page, you suddenly see you have to upload a marked document with all the changes you have made.
This can be a real pain with a word document.
Do you highlight every little change you have made?
Highlighting new text is pretty easy, but how do you show you have deleted some sections?
How do you distinguish between new and revised section.

With LaTeX and git, making such a document is as simple as:

```
$ latexdiff-vc --git -r <tag/hash/branch> document.tex
```

Basically you say, please compare the current state of `document.tex` to whatever it was in a specific commit, which you can specify with a branch, tag, or hash.
This will create a new `tex` file in the same folder, that when compiled will show all additions and deletions in blue and red respectively.
So if you add a tag to the commit of the document that you submitted to the journal, you can very easily create such a difference document.

Branching is great for when you are not sure about the journal.
Each journal likes to be special and demand a specific structure in the paper, and often a unique citation stile.
Let's say you first explore the option of writing the paper for journal 1.
As you are writing you are not really sure anymore journal 1 is the right fit for the study.
When you are using git, you just create a new branch at this point and start writing on that.
After some more writing, perhaps you decide journal 1 was the right fit after all.
You can either go back to the original branch or try to merge the current branch into the original one.
Imagine having to keep track of all these changes with all kinds of versions of Word documents...

Word is great for many applications, but scientific publications are not one of them.
Give LaTeX with git a serious try, and if you find that it works for you try to convince your colleagues!

A final tip: if you add images to version control, it is best to add them separately in different commits or append them as large files.
Images are binary files, so you can't keep track of their changes unfortunately.
If you add them in separate commits or as an annex you can easily remove them from the history later.
This is much harder when you have checked both changes to the text and images simultaneously into history.


