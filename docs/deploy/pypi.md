# Packaging Python Projects

This tutorial walks you through how to package a simple Python project. It will show you how to add the necessary files and structure to create the package, how to build the package, and how to upload it to the Python Package Index (PyPI).

Tip

If you have trouble running the commands in this tutorial, please copy the command and its output, then [open an issue](https://github.com/pypa/packaging-problems/issues/new?template=packaging_tutorial.yml&title=Trouble+with+the+packaging+tutorial&guide=https://packaging.python.org/tutorials/packaging-projects) on the [packaging-problems](https://github.com/pypa/packaging-problems) repository on GitHub. We’ll do our best to help you!

Some of the commands require a newer version of [pip](https://packaging.python.org/en/latest/key_projects/#pip), so start by making sure you have the latest version installed:

[X] Unix/macOS[ ] Windows

```
py -m pip install --upgrade pip
```

## A simple project

This tutorial uses a simple project named `<span class="pre">example_package_YOUR_USERNAME_HERE</span>`. If your username is `<span class="pre">me</span>`, then the package would be `<span class="pre">example_package_me</span>`; this ensures that you have a unique package name that doesn’t conflict with packages uploaded by other people following this tutorial. We recommend following this tutorial as-is using this project, before packaging your own project.

Create the following file structure locally:

```
packaging_tutorial/
└── src/
    └── example_package_YOUR_USERNAME_HERE/
        ├── __init__.py
        └── example.py
```

The directory containing the Python files should match the project name. This simplifies the configuration and is more obvious to users who install the package.

Creating the file `<span class="pre">__init__.py</span>` is recommended because the existence of an `<span class="pre">__init__.py</span>` file allows users to import the directory as a regular package, even if (as is the case in this tutorial) `<span class="pre">__init__.py</span>` is empty. [[1]](https://packaging.python.org/en/latest/tutorials/packaging-projects/#namespace-packages)

`<span class="pre">example.py</span>` is an example of a module within the package that could contain the logic (functions, classes, constants, etc.) of your package. Open that file and enter the following content:

```
def add_one(number):
    return number + 1
```

If you are unfamiliar with Python’s [modules](https://packaging.python.org/en/latest/glossary/#term-Module) and [import packages](https://packaging.python.org/en/latest/glossary/#term-Import-Package), take a few minutes to read over the [Python documentation for packages and modules](https://docs.python.org/3/tutorial/modules.html#packages).

Once you create this structure, you’ll want to run all of the commands in this tutorial within the `<span class="pre">packaging_tutorial</span>` directory.

## Creating the package files

You will now add files that are used to prepare the project for distribution. When you’re done, the project structure will look like this:

```
packaging_tutorial/
├── LICENSE
├── pyproject.toml
├── README.md
├── src/
│   └── example_package_YOUR_USERNAME_HERE/
│       ├── __init__.py
│       └── example.py
└── tests/
```

## Creating a test directory

`<span class="pre">tests/</span>` is a placeholder for test files. Leave it empty for now.

## Choosing a build backend

Tools like [pip](https://packaging.python.org/en/latest/key_projects/#pip) and [build](https://packaging.python.org/en/latest/key_projects/#build) do not actually convert your sources into a [distribution package](https://packaging.python.org/en/latest/glossary/#term-Distribution-Package) (like a wheel); that job is performed by a [build backend](https://packaging.python.org/en/latest/glossary/#term-Build-Backend). The build backend determines how your project will specify its configuration, including metadata (information about the project, for example, the name and tags that are displayed on PyPI) and input files. Build backends have different levels of functionality, such as whether they support building [extension modules](https://packaging.python.org/en/latest/glossary/#term-Extension-Module), and you should choose one that suits your needs and preferences.

You can choose from a number of backends; this tutorial uses [Hatchling](https://packaging.python.org/en/latest/key_projects/#hatch) by default, but it will work identically with [Setuptools](https://packaging.python.org/en/latest/key_projects/#setuptools), [Flit](https://packaging.python.org/en/latest/key_projects/#flit), [PDM](https://packaging.python.org/en/latest/key_projects/#pdm), and others that support the `<span class="pre">[project]</span>` table for [metadata](https://packaging.python.org/en/latest/tutorials/packaging-projects/#configuring-metadata).

Note

Some build backends are part of larger tools that provide a command-line interface with additional features like project initialization and version management, as well as building, uploading, and installing packages. This tutorial uses single-purpose tools that work independently.

The `<span class="pre">pyproject.toml</span>` tells [build frontend](https://packaging.python.org/en/latest/glossary/#term-Build-Frontend) tools like [pip](https://packaging.python.org/en/latest/key_projects/#pip) and [build](https://packaging.python.org/en/latest/key_projects/#build) which backend to use for your project. Below are some examples for common build backends, but check your backend’s own documentation for more details.

[X] Hatchling

```
[build-system]
requires=["hatchling"]
build-backend="hatchling.build"
```

[ ] setuptools[ ] Flit[ ] PDM

The `<span class="pre">requires</span>` key is a list of packages that are needed to build your package. The [frontend](https://packaging.python.org/en/latest/glossary/#term-Build-Frontend) should install them automatically when building your package. Frontends usually run builds in isolated environments, so omitting dependencies here may cause build-time errors. This should always include your backend’s package, and might have other build-time dependencies.

The `<span class="pre">build-backend</span>` key is the name of the Python object that frontends will use to perform the build.

Both of these values will be provided by the documentation for your build backend, or generated by its command line interface. There should be no need for you to customize these settings.

Additional configuration of the build tool will either be in a `<span class="pre">tool</span>` section of the `<span class="pre">pyproject.toml</span>`, or in a special file defined by the build tool. For example, when using `<span class="pre">setuptools</span>` as your build backend, additional configuration may be added to a `<span class="pre">setup.py</span>` or `<span class="pre">setup.cfg</span>` file, and specifying `<span class="pre">setuptools.build_meta</span>` in your build allows the tools to locate and use these automatically.

### Configuring metadata

Open `<span class="pre">pyproject.toml</span>` and enter the following content. Change the `<span class="pre">name</span>` to include your username; this ensures that you have a unique package name that doesn’t conflict with packages uploaded by other people following this tutorial.

```
[project]
name="example_package_YOUR_USERNAME_HERE"
version="0.0.1"
authors=[
{name="Example Author",email="author@example.com"},
]
description="A small example package"
readme="README.md"
requires-python=">=3.8"
classifiers=[
"Programming Language :: Python :: 3",
"License :: OSI Approved :: MIT License",
"Operating System :: OS Independent",
]

[project.urls]
Homepage="https://github.com/pypa/sampleproject"
Issues="https://github.com/pypa/sampleproject/issues"
```

* `<span class="pre">name</span>` is the *distribution name* of your package. This can be any name as long as it only contains letters, numbers, `<span class="pre">.</span>`, `<span class="pre">_</span>` , and `<span class="pre">-</span>`. It also must not already be taken on PyPI. **Be sure to update this with your username** for this tutorial, as this ensures you won’t try to upload a package with the same name as one which already exists.
* `<span class="pre">version</span>` is the package version. (Some build backends allow it to be specified another way, such as from a file or Git tag.)
* `<span class="pre">authors</span>` is used to identify the author of the package; you specify a name and an email for each author. You can also list `<span class="pre">maintainers</span>` in the same format.
* `<span class="pre">description</span>` is a short, one-sentence summary of the package.
* `<span class="pre">readme</span>` is a path to a file containing a detailed description of the package. This is shown on the package detail page on PyPI. In this case, the description is loaded from `<span class="pre">README.md</span>` (which is a common pattern). There also is a more advanced table form described in the [pyproject.toml guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#writing-pyproject-toml).
* `<span class="pre">requires-python</span>` gives the versions of Python supported by your project. An installer like [pip](https://packaging.python.org/en/latest/key_projects/#pip) will look back through older versions of packages until it finds one that has a matching Python version.
* `<span class="pre">classifiers</span>` gives the index and [pip](https://packaging.python.org/en/latest/key_projects/#pip) some additional metadata about your package. In this case, the package is only compatible with Python 3, is licensed under the MIT license, and is OS-independent. You should always include at least which version(s) of Python your package works on, which license your package is available under, and which operating systems your package will work on. For a complete list of classifiers, see [https://pypi.org/classifiers/](https://pypi.org/classifiers/).
* `<span class="pre">urls</span>` lets you list any number of extra links to show on PyPI. Generally this could be to the source, documentation, issue trackers, etc.

See the [pyproject.toml guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#writing-pyproject-toml) for details on these and other fields that can be defined in the `<span class="pre">[project]</span>` table. Other common fields are `<span class="pre">keywords</span>` to improve discoverability and the `<span class="pre">dependencies</span>` that are required to install your package.

## Creating README.md

Open `<span class="pre">README.md</span>` and enter the following content. You can customize this if you’d like.

```
# Example Package

This is a simple example package. You can use
[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.
```

## Creating a LICENSE

It’s important for every package uploaded to the Python Package Index to include a license. This tells users who install your package the terms under which they can use your package. For help picking a license, see [https://choosealicense.com/](https://choosealicense.com/). Once you have chosen a license, open `<span class="pre">LICENSE</span>` and enter the license text. For example, if you had chosen the MIT license:

```
Copyright (c) 2018 The Python Packaging Authority

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Most build backends automatically include license files in packages. See your backend’s documentation for more details.

## Including other files

The files listed above will be included automatically in your [source distribution](https://packaging.python.org/en/latest/glossary/#term-Source-Distribution-or-sdist). If you want to include additional files, see the documentation for your build backend.

## Generating distribution archives

The next step is to generate [distribution packages](https://packaging.python.org/en/latest/glossary/#term-Distribution-Package) for the package. These are archives that are uploaded to the Python Package Index and can be installed by [pip](https://packaging.python.org/en/latest/key_projects/#pip).

Make sure you have the latest version of PyPA’s [build](https://packaging.python.org/en/latest/key_projects/#build) installed:

[X] Unix/macOS[ ] Windows

```
py -m pip install --upgrade build
```

Tip

If you have trouble installing these, see the [Installing Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/) tutorial.

Now run this command from the same directory where `<span class="pre">pyproject.toml</span>` is located:

[X] Unix/macOS[ ] Windows

```
py -m build
```

This command should output a lot of text and once completed should generate two files in the `<span class="pre">dist</span>` directory:

```
dist/
├── example_package_YOUR_USERNAME_HERE-0.0.1-py3-none-any.whl
└── example_package_YOUR_USERNAME_HERE-0.0.1.tar.gz
```

The `<span class="pre">tar.gz</span>` file is a [source distribution](https://packaging.python.org/en/latest/glossary/#term-Source-Distribution-or-sdist) whereas the `<span class="pre">.whl</span>` file is a [built distribution](https://packaging.python.org/en/latest/glossary/#term-Built-Distribution). Newer [pip](https://packaging.python.org/en/latest/key_projects/#pip) versions preferentially install built distributions, but will fall back to source distributions if needed. You should always upload a source distribution and provide built distributions for the platforms your project is compatible with. In this case, our example package is compatible with Python on any platform so only one built distribution is needed.

## Uploading the distribution archives

Finally, it’s time to upload your package to the Python Package Index!

The first thing you’ll need to do is register an account on TestPyPI, which is a separate instance of the package index intended for testing and experimentation. It’s great for things like this tutorial where we don’t necessarily want to upload to the real index. To register an account, go to [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/) and complete the steps on that page. You will also need to verify your email address before you’re able to upload any packages. For more details, see [Using TestPyPI](https://packaging.python.org/en/latest/guides/using-testpypi/).

To securely upload your project, you’ll need a PyPI [API token](https://test.pypi.org/help/#apitoken). Create one at [https://test.pypi.org/manage/account/#api-tokens](https://test.pypi.org/manage/account/#api-tokens), setting the “Scope” to “Entire account”. **Don’t close the page until you have copied and saved the token — you won’t see that token again.**

Now that you are registered, you can use [twine](https://packaging.python.org/en/latest/key_projects/#twine) to upload the distribution packages. You’ll need to install Twine:

[X] Unix/macOS[ ] Windows

```
py -m pip install --upgrade twine
```

Once installed, run Twine to upload all of the archives under `<span class="pre">dist</span>`:

[X] Unix/macOS[ ] Windows

```
py -m twine upload --repository testpypi dist/*
```

You will be prompted for a username and password. For the username, use `<span class="pre">__token__</span>`. For the password, use the token value, including the `<span class="pre">pypi-</span>` prefix.

After the command completes, you should see output similar to this:

```
Uploading distributions to https://test.pypi.org/legacy/
Enter your username: __token__
Uploading example_package_YOUR_USERNAME_HERE-0.0.1-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8.2/8.2 kB • 00:01 • ?
Uploading example_package_YOUR_USERNAME_HERE-0.0.1.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.8/6.8 kB • 00:00 • ?
```

Once uploaded, your package should be viewable on TestPyPI; for example: `<span class="pre">https://test.pypi.org/project/example_package_YOUR_USERNAME_HERE</span>`.

## Installing your newly uploaded package

You can use [pip](https://packaging.python.org/en/latest/key_projects/#pip) to install your package and verify that it works. Create a [virtual environment](https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-and-using-virtual-environments) and install your package from TestPyPI:

[X] Unix/macOS[ ] Windows

```
py -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-package-YOUR-USERNAME-HERE
```

Make sure to specify your username in the package name!

pip should install the package from TestPyPI and the output should look something like this:

```
Collecting example-package-YOUR-USERNAME-HERE
  Downloading https://test-files.pythonhosted.org/packages/.../example_package_YOUR_USERNAME_HERE_0.0.1-py3-none-any.whl
Installing collected packages: example_package_YOUR_USERNAME_HERE
Successfully installed example_package_YOUR_USERNAME_HERE-0.0.1
```

Note

This example uses `<span class="pre">--index-url</span>` flag to specify TestPyPI instead of live PyPI. Additionally, it specifies `<span class="pre">--no-deps</span>`. Since TestPyPI doesn’t have the same packages as the live PyPI, it’s possible that attempting to install dependencies may fail or install something unexpected. While our example package doesn’t have any dependencies, it’s a good practice to avoid installing dependencies when using TestPyPI.

You can test that it was installed correctly by importing the package. Make sure you’re still in your virtual environment, then run Python:

[X] Unix/macOS[ ] Windows

```
py
```

and import the package:

```
>>> from example_package_YOUR_USERNAME_HERE import example
>>> example.add_one(2)
3
```

## Next steps

**Congratulations, you’ve packaged and distributed a Python project!** ✨ 🍰 ✨

Keep in mind that this tutorial showed you how to upload your package to Test PyPI, which isn’t a permanent storage. The Test system occasionally deletes packages and accounts. It is best to use TestPyPI for testing and experiments like this tutorial.

When you are ready to upload a real package to the Python Package Index you can do much the same as you did in this tutorial, but with these important differences:

* Choose a memorable and unique name for your package. You don’t have to append your username as you did in the tutorial, but you can’t use an existing name.
* Register an account on [https://pypi.org](https://pypi.org/) - note that these are two separate servers and the login details from the test server are not shared with the main server.
* Use `<span class="pre">twine</span><span> </span><span class="pre">upload</span><span> </span><span class="pre">dist/*</span>` to upload your package and enter your credentials for the account you registered on the real PyPI. Now that you’re uploading the package in production, you don’t need to specify `<span class="pre">--repository</span>`; the package will upload to [https://pypi.org/](https://pypi.org/) by default.
* Install your package from the real PyPI using `<span class="pre">python3</span><span> </span><span class="pre">-m</span><span> </span><span class="pre">pip</span><span> </span><span class="pre">install</span><span> </span><span class="pre">[your-package]</span>`.

At this point if you want to read more on packaging Python libraries here are some things you can do:

* Read about advanced configuration for your chosen build backend: [Hatchling](https://hatch.pypa.io/latest/config/metadata/), [setuptools](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html "(in setuptools v75.3.0.post20241029)"), [Flit](https://flit.pypa.io/en/stable/pyproject_toml.html "(in Flit v3.9.0)"), [PDM](https://pdm-project.org/latest/reference/pep621/).
* Look at the [guides](https://packaging.python.org/en/latest/guides/) on this site for more advanced practical information, or the [discussions](https://packaging.python.org/en/latest/discussions/) for explanations and background on specific topics.
* Consider packaging tools that provide a single command-line interface for project management and packaging, such as [hatch](https://packaging.python.org/en/latest/key_projects/#hatch), [flit](https://packaging.python.org/en/latest/key_projects/#flit), [pdm](https://packaging.python.org/en/latest/key_projects/#pdm), and [poetry](https://packaging.python.org/en/latest/key_projects/#poetry).

---

Notes

[[1](https://packaging.python.org/en/latest/tutorials/packaging-projects/#id1)]Technically, you can also create Python packages without an `<span class="pre">__init__.py</span>` file, but those are called [namespace packages](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/) and considered an **advanced topic** (not covered in this tutorial). If you are only getting started with Python packaging, it is recommended to stick with *regular packages* and `<span class="pre">__init__.py</span>` (even if the file is empty).

[NextGuides](https://packaging.python.org/en/latest/guides/)[PreviousManaging Application Dependencies](https://packaging.python.org/en/latest/tutorials/managing-dependencies/)

Copyright © 2013–2020, PyPA
