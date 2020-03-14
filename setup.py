import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="stonks",
    version="1.0.0",
    author="georgefahmy",
    author_email="geofahm@gmail.com",
    description="Generate a report or stream live stocks from wallstreetbets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    url="https://github.com/georgefahmy/stonks",
    license="MIT",
    python_requires=">=3.6",
    install_requires=["praw==6.5.1", "textblob==0.15.3", "robin-stocks==0.9.9.6"],
    entry_points={
        "console_scripts": [
            "streamer = streamer:main",
            "wsb_report = wsb_report:main",
            "all_stream = all_stream:main",
        ]
    },
)
