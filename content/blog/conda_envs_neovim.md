Title: Make active conda environment persist in Neovim terminal
Date: 2022-05-23 13:40
Category: Neovim
Tags: vim, Linux, neovim, conda, python
Summary: Small fix in bashrc or zshrc for making conda environments more intuitive

Conda is a package manager and virtual environment manager mainly used in the python ecosystem.
In contrast to other tools, conda environments work with absolute paths, and are usually available system wide instead of only in a project directory.
As a former scientist, I personally like conda for the amount of available non-python software that it makes available. 
It is the one-stop tool with which I can manage environments and different python versions.

For my IDE I use Neovim.
Before beginning development on a project I typically activate the right conda environment in the shell with `conda activate ...` and then start my editor.
I would still like to create something with which I can easily and interactively select and change the right conda environment from within neovim but that's for another time.
This workflow is fine for making neovim "environment aware" so code linting and tools like mypy work.

One annoyance I've had with this flow is that the built-in terminal, accessible via `:term`, does not seem to be conda environment aware.
Launching it will bring up the prompt with the default environment activated, which is kind of annoying since it requires me to run `conda activate ...` again in each shell to activate the right virtual environment.
However, it seems I was misunderstanding what was going on under the hood.
Getting to better grips with how conda works helped me to find a very easy fix.

When `conda` is installed and one runs `conda init`, a snippet of code is inserted into the `bashrc` or `zshrc`.
It looks something like:

```shell
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/din14970/miniconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/din14970/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/din14970/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/din14970/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
```

The snippet will automatically activate the default environment (`base`) when launching a new shell.
When launching the built-in terminal in neovim, this also happens, so it is pretty logical that the default environment is active in a new shell.

However, for the neovim terminal, we can take advantage of the fact that it is launched by the parent process neovim.
Inside the neovim terminal, you can run `ps -e | grep $PPID`, which shows that neovim is the parent.
This means that environment variables from parent processes are passed on to these sessions.
You can test this with `env | grep nvim`, which shows you have access to some environment variables defined by neovim that are inaccessible from the parent shell (access through `CTRL+Z`).
We can abuse this property with `conda` as well.

As it turns out, every time `conda activate ...` is called, a number of environment variables are updated and created.
The implementation works like a stack.
Whenever you call `conda activate ...`, the new environment is pushed onto the stack; calling `conda deactivate` pops the last environment from the stack.
The environment variables created by conda can be queried with `env | grep CONDA`:

```shell
CONDA_EXE=/home/din14970/miniconda3/bin/conda
_CE_CONDA=
CONDA_PYTHON_EXE=/home/din14970/miniconda3/bin/python
CONDA_SHLVL=1
CONDA_PREFIX=/home/din14970/miniconda3
CONDA_DEFAULT_ENV=base
CONDA_PROMPT_MODIFIER=(miniconda3)
```

When activating another environment, say `dev`, the variables change to

```shell
CONDA_EXE=/home/din14970/miniconda3/bin/conda
_CE_CONDA=
CONDA_PYTHON_EXE=/home/din14970/miniconda3/bin/python
CONDA_SHLVL=2
CONDA_PREFIX=/home/din14970/miniconda3/envs/dev
CONDA_DEFAULT_ENV=dev
CONDA_PROMPT_MODIFIER=(dev)
CONDA_PREFIX_1=/home/din14970/miniconda3
```

Whenever we activate a new environment, a new variable `CONDA_PREFIX_<N>` is created that stores the previous environment.
The counter `CONDA_SHLVL` is also incremented by 1.
It turns out that these variables are also passed into the neovim subprocess, and into its child terminal.
But because launching a new terminal calls the conda initialization code in the `bashrc` or `zshrc` again, the `base` environment is pushed onto the stack once more.
Calling `conda deactivate` in the neovim terminal will actually bring us to the right environment.

To avoid this manual step, a very simple solution that seems to work for me so far is wrapping the conda initialization into a simple if statement:

```shell
if [[ -z "${CONDA_SHLVL}" ]]; then
  # >>> conda initialize >>>
  ...
  # <<< conda initialize <<<
fi
```

Basically, it will only run conda initialization when the `CONDA_SHLVL` variable is 0, i.e. when it is not yet defined.
In this way, if neovim is launched with the right virtual environment active, it will pass this along to the child terminal.
