"""Setup script for mcp-powershell-exec."""
from setuptools import setup, find_packages

setup(
    packages=find_packages(),
    package_data={
        "mcp_powershell_exec": ["py.typed"],
    },
)
