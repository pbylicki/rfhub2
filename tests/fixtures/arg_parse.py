import argparse

parser = argparse.ArgumentParser(
    prog="script_for_system_exit", description="I should trigger SystemExit"
)
parser.add_argument("-c", "--conf", required=True)
args = parser.parse_args()
