import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="stonks",
    version="1.0.1",
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
    zip_safe=False,
    python_requires=">=3.6",
    setup_requires=[],
    install_requires=["praw==6.5.1", "textblob==0.15.3", "robin-stocks==0.9.9.6", "pytz==2019.3"],
    classifiers=["Programming Language :: Python :: 3", "Programming Language :: Python :: 3.7",],
    entry_points={
        "console_scripts": [
            "streamer = scripts.streamer:main",
            "wsb_report = scripts.wsb_report:main",
            "all_stream = scripts.all_stream:main",
            "get_symbols = utils.get_symbols:main",
        ]
    },
)
