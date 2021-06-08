# Python Package Management on Windows

Python does not have [good](https://www.reddit.com/r/webdev/comments/46w7gt/is_it_just_me_or_is_package_management_with/) [package](https://news.ycombinator.com/item?id=19985802) [management](https://news.ycombinator.com/item?id=21781604).

Recently I was trying to update one of my Conda environments. After running `conda update --all` however, the environment crashed.

This is not the only problem I have with Conda.

- Many python packages aren't available on Conda. For example, `broadlink`
- Conda sometimes hosts outdated versions of packages vs pip, such as `pdfminer` (that was a real headache)
- Search is slow. Very slow.

![](/static/images/2021-04-15/conda.gif)

That being said, Conda allows you to specify and manage Python itself as a dependency, which is great on Windows, as it prevents you from polluting the working environment.

I started looking for alternatives. There's [virtualenv](https://virtualenv.pypa.io/en/latest/), [poetry](https://python-poetry.org/), [pyenv-win](https://github.com/pyenv-win/pyenv-win) among others.

So what's the best solution?

## Pipenv + Chocolatey to the rescue!

<img style="max-width: min(30vw, 150px);" src="/static/images/2021-04-15/chocolatey.svg" alt="Chocolatey"/>

My setup:

- Chocolatey with `--sidebyside` to manage Python versions
- Pipenv to manage Python packages under a specified Python version

Yup, I decided to use Chocolatey to manage python versions. I don't want to have to keep installing Python 3.8.9 or whatever again and again, just because PyTorch or OpenCV some library doesn't support 3.9.

I switch between Python versions using either `pipenv --python <version>` e.g. `pipenv --python 3.8.9` to set the environment.

You can activate the pipenv shell with `pipenv shell`. Otherwise, some IDEs e.g. PyCharm do this for you automatically.

Subsequently, I use `pipenv install <package>`. If you install packages using `pip` in a `pipenv` environment, they won't appear in the Pipfile, and won't be managed in the dependency graph.

You can list the dependency graph with `pipenv graph`.

Of note, Pipenv is [recommended](https://packaging.python.org/tutorials/managing-dependencies/) by Python itself. It can update all packages installed via pip and manage dependencies. Meanwhile, `conda update --all` doesn't update pip packages...

I know Chocolatey executes administrator-level code on your computer, but it works. I'll have to move to Linux one day, seeing as so many Python packages can't be built on Windows.

## Automatic Dependency Generation

Sometimes you might have a Python project with another dependency management framework, e.g. Conda or Pip.

One day, you realize you need to distribute your project to your friend, but you don't have a list of dependencies.

You could do `pip freeze`, but it's usually full of packages your project doesn't even use.

Here's where automatic dependency generation comes in. Packages like `pipreqs` and `pigar` are able to analyze the source code of your project, and produce a `requirements.txt` automatically.

As to which is the best, `pipreqs` or `pigar`, I've tried both, and `pipreqs` is better than `pigar` for automatically generating the requirements for your project.

