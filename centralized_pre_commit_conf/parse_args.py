import argparse

import confuse


def get_url_from_args(url: str, branch: str, path: str) -> str:
    """Necessary because we don't want to have to handle redirection."""
    if url.endswith("/"):
        url = url[:-1]
    if path.endswith("/"):
        path = path[:-1]
    if path and branch:
        return f"{url}/{branch}/{path}"
    if branch:
        return f"{url}/{branch}"
    if path:
        return f"{url}/{path}"
    return f"{url}"


def parse_args(config) -> confuse.Configuration:
    parser = argparse.ArgumentParser(description=__doc__)
    sub_parser = parser.add_subparsers()
    install = sub_parser.add_parser("install", help="Install the configuration from a server")
    install_parse_args(config, install)
    configu = sub_parser.add_parser("set-conf", help="Permit to set the configuration")
    auto_apply = sub_parser.add_parser("auto-apply", help="Apply all the possible automatic tools.")
    args = parser.parse_args()
    config.set_args(args)
    return config


def install_parse_args(config, install):
    install.add_argument("-u", "--url", default=config["repository"].get(), help="Git repository URL")
    install.add_argument("-b", "--branch", default=config["branch"].get("str"), help="Git branch")
    install.add_argument("-p", "--path", default=config["path"].get(), help="Path inside the git repository")
    default_files = config["configuration_files"].get(list)
    install.add_argument("-c", "--configuration-files", nargs="+", default=default_files, help="Files to recover")
    default_replace = config["replace_existing"].get(bool)
    install.add_argument(
        "-f", "--replace-existing", default=default_replace, action="store_true", help="Replace the existing file?"
    )
    install.add_argument("--no-replace-existing", dest="replace_existing", action="store_false")
    default_verbose = config["verbose"].get(bool)
    install.add_argument(
        "-v", "--verbose", default=default_verbose, action="store_true", help="Display additional information?"
    )
    install.add_argument("--no-verbose", dest="verbose", action="store_false")
