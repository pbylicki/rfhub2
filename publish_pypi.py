import os
from pkg_resources import parse_version
import requests

from rfhub2.version import version


def get_pypi_version() -> str:
    resp = requests.get("https://pypi.org/pypi/rfhub2/json")
    assert resp.status_code == 200
    return resp.json()["info"]["version"]


def execute_cmd(cmd: str):
    print(f"Executing command '{cmd}'")
    os.system(cmd)


def publish_to_pypi() -> None:
    execute_cmd("twine upload dist/*")
    execute_cmd("rm -rf build dist rfhub2.egg-info")


def should_publish() -> bool:
    return os.getenv("TRAVIS_BRANCH", "") == "master" and os.getenv("TRAVIS_PULL_REQUEST", "") == "false"


if __name__ == "__main__":
    local_version = parse_version(version)
    print(f"Found local version: {local_version}")
    pypi_version = parse_version(get_pypi_version())
    print(f"Found PyPI version: {pypi_version}")
    if local_version > pypi_version and should_publish():
        publish_to_pypi()
    else:
        print("Local version is not greater than PyPI version, publishing skipped")
