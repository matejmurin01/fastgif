from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="fastgif",
    version="1.1",
    description="Matplotlib GIF maker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matejmurin01/fastgif",
    author="Matej Murín",
    author_email="matejmurin01@gmail.com",
    license="Apache License 2.0",
    keywords=[
        "gif",
        "gifs",
        "animation",
        "matplotlib",
    ],
    py_modules=["fastgif"],
    python_requires=">=3.8.12",
    install_requires=[
        "matplotlib>=3.5.0",
        "imageio>=2.9.0"
    ]
)
