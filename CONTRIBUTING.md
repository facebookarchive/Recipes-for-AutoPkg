# Contributing to Facebook's AutoPkg Recipes
We want to make contributing to this project as easy and transparent as
possible.

## Our Development Process
Changes to AutoPkg recipes must be tested extensively and follow [AutoPkg recipe best practices](https://github.com/autopkg/autopkg/wiki/Recipe-Writing-Guidelines) as best as possible.

These recipes are authored to support Facebook's needs first and foremost, and are then made available to the community in the hopes that others may benefit.

Changes may occur in these recipes as Facebook encounters new solutions or revised methods for obtaining and installing the software.

## Pull Requests
We actively welcome your pull requests.

1. Fork the repo and create your branch from `master`.
2. If you've added code that should be tested, please extensively test it and demonstrate with run logs that it works.
3. If any input or output variables change, please update the documentation.
4. Obviously, your recipe changes should work.
5. Make sure your code passes lint tests.
6. If you haven't already, complete the Contributor License Agreement ("CLA").

## Contributor License Agreement ("CLA")
In order to accept your pull request, we need you to submit a CLA. You only need
to do this once to work on any of Facebook's open source projects.

Complete your CLA here: <https://code.facebook.com/cla>

## Issues
We use GitHub issues to track public bugs. Please ensure your description is
clear and has sufficient instructions to be able to reproduce the issue.

Facebook has a [bounty program](https://www.facebook.com/whitehat/) for the safe
disclosure of security bugs. In those cases, please go through the process
outlined on that page and do not file a public issue.

## Coding Style
* 4 spaces for indentation rather than tabs
* 80 character line length
* All custom processors (Python code) must pass flake8 and isort style linting.

Sometimes custom processors are necessities to solve specific problems that can't be addressed by the built in provided processors. This repo contains several custom processors for that purpose.

When possible, utilize existing built-in processors and shared processors.  Custom Python processors should be purpose-built and limited in scope to the functionality necessary to solve the problem.

## License
By contributing to Facebook's Recipes for AutoPkg, you agree that your contributions will be licensed
under its BSD license.

Please note that most of AutoPkg itself is licensed under the Apache license. For a good source on the differences between these licenses, please consult the free open book "[Understanding Open Source and Free Software Licensing](http://www.oreilly.com/openbook/osfreesoft/)" (O'Reilly, 2004).
