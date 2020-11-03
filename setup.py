
import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
        name = "ccfeeder",
        version = "0.0.1",
        author = "Peder G. Landsverk",
        author_email = "pglandsverk@gmail.com",
        description = "Webapp support tools",
        long_description = long_description,
        long_description_content_type="text/markdown",
        url = "https://www.github.com/prio-data/ccfeeder",
        packages = setuptools.find_packages(),
        scripts=[
            "bin/ccfeeder",
            ],
        python_requires=">=3.8",
        install_requires=[
            "pydantic>=1.7.2",
            "Fiona==1.8.17",
            "fire>=0.3.1",
            "topojson==1.0rc11",
            "requests==2.24.0"
        ]
    )
