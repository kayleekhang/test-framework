import argparse
from pathlib import Path
from tools._common import add_common, load_system

def main():
    parser = argparse.ArgumentParser()
    add_common(parser)
    parser.add_argument("--out", default="artifacts/builds")
    args = parser.parse_args()

    system = load_system(args)
    results = system.build(Path(args.out))
    print(f"Built {system.config.system_name}")
    for product, product_results in results.items():
        print(f"- {product}")
        for result in product_results:
            print(f"  {result.artifact}")

if __name__ == "__main__":
    main()
