import yaml
import json
import os
import sys

workdir = sys.argv[1]

with open(f"{workdir}/.git/info/sparse-checkout", "r") as f:
    x = filter(lambda x: x.startswith("trains/"), f.readlines())
    sparse_apps = [x.strip() for x in x]

catalog = {}

for c in sparse_apps:
    _, train, app, _ = c.split("/")
    if train not in catalog:
        catalog[train] = []
    catalog[train].append(app)

with open(f"{workdir}/catalog.json", "r") as f:
    full_catalog = json.load(f)

for k in list(full_catalog.keys()):
    if k not in catalog.keys():
        full_catalog.pop(k, None)

for train in list(full_catalog.keys()):
    for app in list(full_catalog[train].keys()):
        if not app in catalog[train]:
            full_catalog[train].pop(app, None)

with open(f"{workdir}/catalog_stripped.json", "w") as f:
    json.dump(full_catalog, f, indent=4)

os.rename(f"{workdir}/catalog.json", f"{workdir}/catalog_full.json")
os.rename(f"{workdir}/catalog_stripped.json", f"{workdir}/catalog.json")

