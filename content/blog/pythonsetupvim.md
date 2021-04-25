Title: Debugging python in neovim
Date: 2021-04-24 13:40
Category: Python
Tags: software, debugging, vim, neovim, pytest, python
Summary: Options for debugging python code when developing in neovim


There are many conveniences of using IDE's like VS Code or PyCharm for coding.
One of them is convenient built-in debugging.
For a variety of reasons detailed [here]({filename}./editorprogression.md), I stubbornly refuse to use these tools and instead want to do all my coding and text-editing in neovim.
Making neovim behave like a decent IDE requires a bit of configuration, so this post deals with the options for integrated debugging for python (some ideas may transfer to other languages).

I must confess that despite writing python code for a number of years, I still mostly debug using print statements and copying blocks of code into Jupyter notebooks.
Usually my development process starts by trying things in a notebook.
Once it starts working, I throw it into a proper project structure. 
Then I go back to the notebook with problematic pieces of code or add print statements to iron out problems.
The problem with print statements is that one has to constantly update them and re-run the program if one is not printing the variables from which one can deduce the problem.
Jupyter notebooks are handy for quick testing and iteration, but as the code blocks grow it becomes difficult to retain an overview.

There must be a better way, so I looked a bit into debuggers and how I could integrate them into my workflow.
A very nice article on this topic can be found on [jdhao's blog](https://jdhao.github.io/2019/01/16/debug_python_in_terminal/).

## Pdb, ipdb and pudb
The most minimal python debugger `pdb` is shipped with python, check the documentation [here](https://docs.python.org/3/library/pdb.html).
It is good to be familiar with this debugger since it will be available wherever python 3 is available.
In the python code you can add:

```python
import pdb

pdb.set_trace()  # put this wherever you want to stop and walk through = breakpoint
```

Since python 3.7 you can also just add `breakpoint()` in the code, which is a built-in function that makes this slightly easier.
Starting the script on the command line will then invoke the debugger.

You can also directly run the code in debug mode using:

```bash
$ python -m pdb script.py
```

Once you are inside `pdb`, you can use the following commands:

* `h`: help, see the most common commands
* `w`: show the stack trace (functions that have been called up to that point)
* `b` [line number, function]: add a breakpoint at a line number or function
* `s` and `n`: step and next, very similar, execute a line. `s` will step into functions, following the stack, `n` will stay at the same level. Note that with `s` you will walk all the way down the rabbit hole if you call functions from some library like numpy.
* `u` and `d`: go up and down the stack trace respectively. Suppose you stepped into some function but you don't care anymore about the details, you go a level `up` and continue with `s` and `n`.
* `r` and `c`: continue until the return value of the current function or until the next break point.
* `j` [line number]: jump to a certain line in the code to be executed next. This allows you to skip or jump over code. It does not go back in time. For that you need `restart`.
* `l`: show where you are in the code
* `q`: quit
* `p` and `pp` [expression]: print and evaluate some expression, you can use variables from the code.

If you just press enter, the last command you entered will be executed.
A couple more interesting ones are `interact` which will launch a REPL with all the variables ready in memory, and `display` which will print the value of an expression every time it is changed in the code.
`pdb` does not have autocomplete (for finding expressions, variables, function names, ...) and no syntax highlighting.
Hence, slightly more friendly is `ipdb` which does have these things built in.
`ipdb` also shows context each time you make a step in the code.
Otherwise the functionality is pretty similar.
You must install `ipdb` with pip though.

`pudb` is offers a nearly graphical debugger in the terminal, showing variables, call stack, breakpoints, a terminal and the progression in the code.
The advantage is that you can directly see everything and don't need to enter commands to view variables.
Also, you can use the `k` and `j` keys to move and select lines to set breakpoints.
Pudb must also be pip installed and is called the same way as pdb and ipdb.

How does one use these tools in (neo)vim?
There are basically two options:

* Open a new window/split/tab, open a terminal there with `:term` and then just run the commands appropriate.
* Suspend vim with `<C-z>` or `:sus`, run the debugger or any other code, then bring back vim with `fg<CR>` (foreground).

### Integration with pytest
Of course this workflow is only helpful when the python program can actually be *run*, i.e. there is some `main` function.
It is not really helpful when you mainly write libraries that don't have a `main` entry point, and really don't do anything when you "run" the file.
Debugging in this case may be most helpful when used in conjunction with unit tests.
These days the most popular python unit test framework is undoubtedly [py.test](https://docs.pytest.org/).
Fortunately pytest integrates with `pdb` directly using the `--pdb` flag.
You can also install a [pytest plugin](https://pypi.org/project/pytest-pudb/) which offers the `--pudb` option to use the pudb debugger instead.
In any case you can add `import pdb; pdb.set_trace()` (or equivalent for ipdb or pudb) in the code and run pytest with the `-s` flag so that stdin and stdout remain accessible; normally pytest captures this.
The downside is that you must modify the code for debugging.

#### Example
Suppose you have some specific function you want to test in the file `demo.py`

```python
### demo.py

def function(a, b):
    a += 1
    b -= 2
    return a + b
```

You have another file `test_demo.py` in the same folder, in which there exists a unit test for `function`.
For pytest, all names of test modules and functions should be preceded with `test_` and names of test classes should be preceded with `Test`.

```python
### test_demo.py

from . import demo

def test_function()
    val = demo.function(2, 3)
    assert val == 5
```

This will obviously give an error. If we only care about this function and this test, we can run and debug this specific test using

```sh
$ pytest --pdb test_demo.py::test_function
```

[This StackOverflow post](https://stackoverflow.com/questions/36456920/is-there-a-way-to-specify-which-pytest-tests-to-run-from-a-file) provides a handy overview of ways to invoke different tests with pytest.
Unfortunately you will only be dropped into pdb (or pudb if you use `--pudb` and have the extension installed) once the exception hits, so you can no longer step through the function where the error may be.
Stack traces with pytest will also be nearly incomprehensible.
Alternatives could be:

* adding the tests that are failing at the bottom of the test module inside a `if __name__ == "__main__":` scope and then running the test module using `python -m pdb test_demo.py`
* adding a `breakpoint()` at the beginning of the test to drop into the debugger.

## Vimspector
So far all the tools described are specific to python and do not really depend on vim at all.
A pretty cool looking project is [vimspector](https://github.com/puremourning/vimspector), a debugger that integrates directly in vim and supports multiple languages.
What is also very cool is that it supports remote debugging (debugging code written and running on a remote host).
However, using it effectively is a bit more involved. 
I haven't played with it extensively yet but to get started the gist is the following:

#### Install Vimspector as a plug-in
I am using plug. In the vimrc I added the following and called `:PlugInstall`.

```vim
let g:vimspector_enable_mappings='HUMAN'

call plug#begin('~/.vim/plugged')

Plug 'puremourning/vimspector'
call plug#end()
```

The `HUMAN` keymaps set the following keys to the following commands (they are quite clunky and I might remap later):

* `F5`: start debugging or continue
* `F3`: stop debugging
* `F4`: restart with same configuration
* `F6`: pause debugging
* `F9`: Toggle a breakpoint on the current line (more or less `b` in pdb)
* `F10`: step over (more or less equal to `n` in pdb)
* `F11`: step into (more or less equal to `s` in pdb)
* `F12`: step out (more or less equal to `u` in pdb)

The readme recommends to add a mapping for `<plug>VimspectorBalloonEval` which evaluates the selected expression, but I couldn't get this to work

```vim
" for normal mode mode
nmap <Leader>di <Plug>VimspecturBalloonEval
" for visual mode
xmap <Leader>di <Plug>VimspecturBalloonEval
```

#### Install the necessary adapters
These actually which actually talk to the debugger. Just in case I installed the adapters for C/C++, Rust, Go, Python and Lua. Check the table on the [Github readme](https://github.com/puremourning/vimspector) and install with

```vim
:VimspectorInstall <adapter>
```

#### Create a .vimspector.json
The key aspect is creating a `.vimspector.json` file in the project directory, which tells the debugger how it should behave. No config file means no debugging. Since I haven't fully delved into the documentation and options for this file, I for now just copied and adapted the easiest configuration I could find from [here](https://github.com/puremourning/vimspector/blob/master/support/test/python/multiple_files/.vimspector.json).

```json
{
    "configurations": {
        "run": {
            "adapter": "debugpy",
            "default": true,
            "configuration": {
                "request": "launch",
                "type": "python",
                "cwd": "${workspaceRoot}",
                "stopOnEntry": true,
                "program": "${file}"
            },
            "breakpoints": {
                "exception": {
                    "raised": "N",
                    "uncaught": "",
                    "userUnhandled": ""
                }
            }
        }
    }
}
```

Pressing `F5` will open the vimspector tab and start debugging.
It can be stopped with `F3` and quit with `:call vimspector#Reset()` (obviously you might want to remap this to something easier).
Don't just close the tab with `:tabclose`, I ran into some issues.
For now I haven't found a very good way to make this work with pytest unfortunately, though I found [this configuration](https://github.com/sagi-z/vimspectorpy) and may update later.
A nice complementary video to check out on vimspector can be found on the Primeagen's channel [here](https://www.youtube.com/watch?v=AnTX2mtOl9Q).

The biggest downside to Vimspector in my view is that it relies on adapters made by companies like Microsoft that send telemetry data.
So the case for using neovim versus something like VSCode is severely diminished when using this tool.
