import argparse
from pathlib import Path
from framework.factory.config_loader import ConfigLoader
from framework.factory.system_factory import SystemFactory

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", choices=["vm", "amd64", "arm64"], default=None)
    parser.add_argument("--out", default="build")
    args = parser.parse_args()

    config = ConfigLoader.load_system(args.config, target_override=args.target)
    system = SystemFactory.create(config)

    output_dir = Path(args.out) / config.system_name / config.target
    artifacts = system.build(output_dir)

    print(f"Built system: {config.system_name}")
    print(f"System target override: {config.target}")
    for product, paths in artifacts.items():
        print(f"- {product}")
        for path in paths:
            print(f"  - {path}")

if __name__ == "__main__":
    main()
