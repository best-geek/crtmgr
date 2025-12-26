import argparse
from os import environ

def resolve_config_file(type):
    
    DEFAULTS = {
        "app":"config.conf",
        "syslog":"syslog_config.conf"
        }
    
    if environ.get(f"CONF_{type.upper()}") is not None:
        return environ.get(f"CONF_{type.upper()}")
    
    return DEFAULTS.get(type, "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", help="The type of config to return",type=str, required=True)


    args = parser.parse_args()

    print(resolve_config_file(args.type))