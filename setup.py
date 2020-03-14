import setuptools

setuptools.setup(
    name="stonks",
    version="1.0.0",
    author="georgefahmy",
    description="Generate a report or stream live stocks from wallstreetbets",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    url="https://github.com/georgefahmy/stonks",
    install_requires=["praw==6.5.1", "textblob==0.15.3", "robin-stocks==0.9.9.6"],
    entry_points={
        "console_scripts": [
            "streamer = streamer:main",
            "wsb_report = wsb_report:main",
            "all_stream = all_stream:main",
        ]
    },
)
