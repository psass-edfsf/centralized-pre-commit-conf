"""This script permit to set up the repository (.gitignore, tox.ini, gitlab-ci.yml) for the whole team."""

import argparse
import os
import sys

import ruamel.yaml

from centralized_pre_commit_conf.constants import ExitCode
from centralized_pre_commit_conf.update_gitignore import update_gitignore

yaml = ruamel.yaml.YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

GITLAB_URL = "http://scm.mrs.antidot.net/general/antidhooks/raw/master/"

TO_ADD_TO_GIT_IGNORE = [".tox/"]

PYTHON_LINT_NAME = "python-lint"
BASE_SCRIPT = [
    "pip3 install tox",
    "curl {remote_url}.flake8 -O",
    "curl {remote_url}.pylintrc -O",
    "curl {remote_url}.isort.cfg -O",
]
LINT_COMMANDS = [
    "black {source_directories} --check --line-length=120",
    "isort -rc {source_directories} --check-only",
    "flake8 {source_directories}",
    "# --errors-only   In error mode, checkers without error messages are,",
    "#                 disabled and for others, only the ERROR messages are",
    "#                 displayed, and no reports are done by default.",
    "pylint {source_directories} --errors-only",
    "# --exit-zero         Always return a 0 (non-error) status code, even if",
    "#                     lint errors are found. This is primarily useful in",
    "#                     continuous integration scripts.",
    "pylint {source_directories} --exit-zero",
]

TOX_SCRIPT = ["tox -e formatting"]


def get_list_of_lint_commands(args, commands) -> []:
    formatted_commands = []
    for command in commands:
        formatted_commands.append(command.format(remote_url=GITLAB_URL, source_directories=args.source_dir))
    return formatted_commands


def create_gitlab_ci_script(args, has_tox=False):
    job = {"stage": "you-can-parallelize-this-lint", "image": "python:3.6", "script": None}
    script = get_list_of_lint_commands(args, BASE_SCRIPT)
    if has_tox:
        script += TOX_SCRIPT
    else:
        script += get_list_of_lint_commands(args, LINT_COMMANDS)
    job["script"] = script
    return job


def create_tox_content(args):
    tox_content = """
[testenv:formatting]
basepython = python3
deps =
"""
    for dependency in dependencies:
        tox_content += "    {}\n".format(dependency)
    tox_content += "commands =\n"
    for command in get_list_of_lint_commands(args, LINT_COMMANDS):
        tox_content += "    {}\n".format(command)
    tox_content += "changedir = {toxinidir}\n"
    return tox_content


def create_tox_file(args):
    tox_ini_path = "tox.ini"
    try:
        with open(tox_ini_path) as f:
            content = f.read()
    except FileNotFoundError:
        content = ""
    if "[testenv:formatting]" in content:
        print("Won't update the tox.ini the job <formatting> already exists.")
        return
    content += create_tox_content(args)
    with open(tox_ini_path, "w") as f:
        if args.verbose:
            print("Creating the tox job 'formatting'")
        f.write(content)


def update_gitlab_ci(args):
    gitlab_yaml_path = ".gitlab-ci.yml"
    with open(gitlab_yaml_path) as f:
        gitlab_ci_yaml = yaml.load(f)
    has_tox = os.path.exists("tox.ini")
    if not gitlab_ci_yaml.get(PYTHON_LINT_NAME):
        gitlab_ci_yaml[PYTHON_LINT_NAME] = create_gitlab_ci_script(args, has_tox)
    else:
        print("Won't update the gitlab-ci.yml the job <{}> already exists.".format(PYTHON_LINT_NAME))
        return
    with open(gitlab_yaml_path, "w") as f:
        yaml.dump(gitlab_ci_yaml, f)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", default=".", help="Source directories where lint should be enforced.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    message = "Install with the following options : {}".format(args)
    if args.verbose:
        print(message)
    update_gitignore(args, configuration_files + TO_ADD_TO_GIT_IGNORE)
    update_gitlab_ci(args)
    create_tox_file(args)


if __name__ == "__main__":
    main()
    sys.exit(ExitCode.OK)
