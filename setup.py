""" common setup for root and portions (modules or sub-packages) of the ae namespace package.

# THIS FILE IS EXCLUSIVELY MAINTAINED
"""
import pprint
from de.setup_project import project_env_vars
from setuptools import setup

INI_PEV = project_env_vars(from_setup=True)

if __name__ == '__main__':
    print("#  EXECUTING SETUPTOOLS SETUP #################################")
    setup_kwargs = INI_PEV['setup_kwargs']
    print(pprint.pformat(setup_kwargs, indent=3, width=75, compact=True))
    setup(**setup_kwargs)
    print("#  FINISHED SETUPTOOLS SETUP  #################################")
