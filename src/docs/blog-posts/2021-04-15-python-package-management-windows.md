# Python Package Management on Windows

Recently I was trying to update one of my Conda environments. After running `conda update --all` however, the environment crashed.

Other than this, there are a few more problems with Conda:

- many python packages aren't available on Conda. For example, `broadlink`
- Conda sometimes hosts outdated versions of packages vs pip, such as `pdfminer` (that was a real headache)
- Search is slow

However, Conda allows you to specify and manage Python itself as a dependency, which is great on Windows, as it prevents you from polluting the environment.

# Pipenv

Pipenv is [recommended](https://packaging.python.org/tutorials/managing-dependencies/) by Python itself. It can update all packages installed via pip and manage dependencies. Meanwhile, `conda update --all` doesn't update pip packages...

However, it requires a base Python installation. On Windows, version management for Python is a headache...

I finally settled around to using [Chocolatey](https://chocolatey.org/) to manage Python itself as a dependency. Granted, there are several problems, the largest being that Chocolatey executes administrator-level code on your computer, but at least it does the job.

My current plan now is to use Chocolatey to manage Python versions, and then use `pipenv` to create virtualenvs for each project.

# Automatic Dependency Generation

I've tried both, and pipreqs is better than pigar for automatically generating the requirements for your project.

