from tomllib import load

with open(r"settings\config.toml", 'rb') as f:
    print(load(f))
