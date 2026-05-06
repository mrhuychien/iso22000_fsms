from setuptools import find_packages, setup

with open("requirements.txt") as f:
	install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
	name="iso22000_fsms",
	version="1.0.0",
	description="Hệ thống quản lý ATTP theo ISO 22000:2018",
	author="Công ty CP Hoàng Giang",
	author_email="hoanggiavn.vn@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
