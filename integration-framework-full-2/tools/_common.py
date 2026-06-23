import argparse
from framework.factory.config_loader import ConfigLoader
from framework.factory.system_factory import SystemFactory

def load_system(args):
    config = ConfigLoader.load_system(args.config, target_override=args.target)
    return SystemFactory.create(config)

def add_common(parser):
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", default=None)

