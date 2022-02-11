# Contributing to
All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.
We recommend going through the list of [`issues`](https://github.com/pyomeca/bioptim/issues) to find issues that interest you, preferable those tagged with `good first issue`.
You can then get your development environment setup with the following instructions.

## Forking

You will need your own fork to work on the code.
Go to the main page and hit the `Fork` button.
You will want to clone your fork to your machine:

```bash
git clone https://github.com/MieuxVoter/majority-judgment-tracker.git
```


## Implementing new features

todo

## Testing your code

todo

## Commenting

Every function, class and module should have their respective proper docstrings completed.
The docstring convention used is NumPy.

## Convention of coding

Please try to follow as much as possible the PEP recommendations (https://www.python.org/dev/peps/). 
Unless you have good reasons to disregard them, your pull-request is required to follow these recommendations. 
I won't get into details here, if you haven't yet, you should read them :) 

All variable names that could be plural should be written as such.

Black is used to enforce the code spacing. 
Please lint with the 120-character max per line's option. 
This means that your pull-request tests on GitHub will appear to fail if black fails (not yet). 
The easiest way to make sure black is happy is to locally run this command:
```bash
black . -l120 --exclude "external/*"
```
If you need to install black, you can do it via conda using the conda-forge channel.
