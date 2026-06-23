import argparse
from tools._common import add_common, load_system

def main():
    parser = argparse.ArgumentParser()
    add_common(parser)
    args = parser.parse_args()

    system = load_system(args)
    system.startup()
    print(f"Launched {system.config.system_name}")

if __name__ == "__main__":
    main()
