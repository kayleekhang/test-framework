import argparse
from tools._common import add_common, load_system

def main():
    parser = argparse.ArgumentParser()
    add_common(parser)
    args = parser.parse_args()

    system = load_system(args)
    system.build()
    results = system.deploy()
    print(f"Deployed {system.config.system_name}")
    for product in results:
        print(f"- {product}")

if __name__ == "__main__":
    main()
