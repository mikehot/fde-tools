from setuptools import setup, find_packages

setup(
    name="fde-tools",
    version="1.0.0",
    author="Jacky Chou (周亚杰)",
    author_email="mikehot668@gmail.com",
    description="Field Deployed Engineer & Applied AI Industrial Automation CLI Toolkit",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mikehot/fde-tools",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        # Zero mandatory heavy dependencies! Optional: pillow for advanced perceptual image hashing
    ],
    extras_require={
        "full": ["pillow>=10.0.0", "mcp>=1.0.0", "pydantic>=2.0.0"]
    },
    entry_points={
        "console_scripts": [
            "fde=fde_tools.cli:main",
            "fde-tools=fde_tools.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
