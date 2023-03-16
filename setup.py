from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in frappe_replicache/__init__.py
from frappe_replicache import __version__ as version

setup(
	name="frappe_replicache",
	version=version,
	description="replicache integration for frappe",
	author="thl1g15",
	author_email="thl1g15@outlook.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
