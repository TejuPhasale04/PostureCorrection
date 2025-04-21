from setuptools import setup, find_packages

setup(
    name='PostureCorrection',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "pandas",
        "requests",
        "plotly",
        "Pillow",
        "streamlit"
    ],
    author="Tejaswini Phasale",
    description="Smart Posture Correction Dashboard App",
)
