<!--
  THIS FILE IS EXCLUSIVELY MAINTAINED IN THE NAMESPACE ROOT PACKAGE. CHANGES HAVE TO BE DONE THERE.
  All changes will be deployed automatically to all the portions of this namespace package.
-->
# base portion of ae namespace package

[![GitLabPipeline](https://img.shields.io/gitlab/pipeline/ae-group/ae_base/master?logo=python)](
    https://gitlab.com/ae-group/ae_base)
[![PyPIVersion](https://img.shields.io/pypi/v/ae_base)](
    https://pypi.org/project/ae-base/#history)

>The portions (modules and sub-packages) of the Application Environment for Python are within
the `ae` namespace and are providing helper methods and classes for to develop
full-featured applications with Python.

[![Coverage](https://ae-group.gitlab.io/ae_base/coverage.svg)](
    https://ae-group.gitlab.io/ae_base/coverage/ae_base_py.html)
[![MyPyPrecision](https://ae-group.gitlab.io/ae_base/mypy.svg)](
    https://ae-group.gitlab.io/ae_base/lineprecision.txt)
[![PyLintScore](https://ae-group.gitlab.io/ae_base/pylint.svg)](
    https://ae-group.gitlab.io/ae_base/pylint.log)

[![PyPIImplementation](https://img.shields.io/pypi/implementation/ae_base)](
    https://pypi.org/project/ae-base/)
[![PyPIPyVersions](https://img.shields.io/pypi/pyversions/ae_base)](
    https://pypi.org/project/ae-base/)
[![PyPIWheel](https://img.shields.io/pypi/wheel/ae_base)](
    https://pypi.org/project/ae-base/)
[![PyPIFormat](https://img.shields.io/pypi/format/ae_base)](
    https://pypi.org/project/ae-base/)
[![PyPIStatus](https://img.shields.io/pypi/status/ae_base)](
    https://libraries.io/pypi/ae-base)
[![PyPIDownloads](https://img.shields.io/pypi/dm/ae_base)](
    https://pypi.org/project/ae-base/#files)


## installation


Execute the following command for to use the ae.base module in your
application. It will install ae.base into your python (virtual) environment:
 
```shell script
pip install ae-base
```

If you instead want to contribute to this portion then first fork
[the ae_base repository at GitLab](https://gitlab.com/ae-group/ae_base "ae.base code repository"),
then pull it to your machine and finally execute the following command in the root folder
of this repository (ae_base):

```shell script
pip install -e .[dev]
```

The last command will install this module portion into your virtual environment, along with
the tools you need to develop and run tests or for to extend the portion documentation.
For to contribute only to the unit tests or the documentation of this portion replace
the setup extras key `dev` in the above command with `tests` or `docs` respectively.


## namespace portion documentation

More info on the features and usage of this portion are available at
[ReadTheDocs](https://ae.readthedocs.io/en/latest/_autosummary/ae.base.html#module-ae.base
"ae_base documentation").

<!-- Common files version 0.1.61 deployed version 0.1.0 (with 0.1.61)
     to https://gitlab.com/ae-group as ae_base module as well as
     to https://ae-group.gitlab.io with CI check results as well as
     to https://pypi.org/project/ae-base as namespace portion ae-base.
-->
