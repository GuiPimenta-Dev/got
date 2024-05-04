from setuptools import setup, find_packages

setup(
    name="got-cli",
    version="0.0.13",
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "openai==1.25.1",
        "groq==0.5.0",
        "click==8.1.3",
        "python-dotenv==1.0.1",
        "inquirerpy==0.3.4",
        "prompt-toolkit==3.0.43"
    ],
    include_package_data=True,
    package_data={
        "got": [
            "prompts/*"
        ],
    },
    author="Guilherme Alves Pimenta",
    author_email="guialvespimenta27@gmail.com",
    description="Got is a library to help you make consistent commit messages with help of AI",
    entry_points={"console_scripts": ["got=got.cli:got"]},
    url="https://github.com/GuiPimenta-Dev/got"
)
