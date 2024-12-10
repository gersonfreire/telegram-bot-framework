Here is a setup.py file for the TlgBotFwk (or tlgfwk) package, which you can use to install the package globally on your Windows Python libraries folder:

```python
from setuptools import setup, find_packages

setup(
    name='tlgfwk',
    version='0.8.7',
    description='A Telegram Bot Framework for monitoring remote hosts',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/tlgfwk',  # Replace with your repository URL
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot>=20.0a4',
        'python-dotenv>=0.21.0',
        'httpx>=0.23.0',
        'cryptography>=3.4.7',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
```

### Explanation:

name

: The name of the package.

- `version`: The version of the package.
- `description`: A short description of the package.
- `author`: The name of the author.
- `author_email`: The email of the author.
- url

: The URL of the package's repository (replace with your actual repository URL).

- `packages`: Automatically find all packages in the directory.
- `install_requires`: A list of dependencies required by the package.
- `classifiers`: A list of classifiers that provide some additional metadata about the package.
- `python_requires`: Specifies the Python versions supported by the package.

### Steps to Install the Package Globally:

1. **Ensure you have the necessary files**: Make sure you have the *setup.py* file in the root directory of your *tlgfwk* library.
2. **Open Command Prompt as Administrator**: To install a package globally, you need administrative privileges. Right-click on the Command Prompt icon and select "Run as administrator".
3. Navigate to the directory containing setup.py: Use the `cd` command to navigate to the directory where your *setup.py* file is located. For example:

```sh
   cd path\to\tlgfwk
```

4. **Install the library globally**: Run the following command to install the library globally:
   ```sh
   python setup.py install
   ```

Alternatively, you can use `pip` to install the library globally:

1. **Create a source distribution**: Run the following command to create a source distribution of your library:

   ```sh
   python setup.py sdist
   ```
2. **Install the library using `pip`**: Use `pip` to install the library globally. Replace

path\to\dist\tlgfwk-0.8.7.tar.gz

 with the actual path to the generated distribution file:

```sh
   pip install path\to\dist\tlgfwk-0.8.7.tar.gz
```

This will install the

tlgfwk

 library globally on your Windows machine, making it available for use in any Python script.
