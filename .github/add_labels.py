import yaml
import os
import sys
import glob
import re
import copy

workdir = sys.argv[1]

paths = {"ix_values": [], "questions": []}
for root, dirs, files in os.walk(workdir):
    for file in filter(lambda x: "ix_values.yaml" in x, files):
        paths["ix_values"].append(os.path.join(root, file))
    for file in filter(lambda x: "questions.yaml" in x, files):
        paths["questions"].append(os.path.join(root, file))

app_pat = re.compile(r".+/trains/([^/]+)/([^/]+)/.+")
container_names = {}

for path in paths["ix_values"]:
    m = app_pat.search(path)
    train, app_name = m.groups()
    with open(path, "r") as f:
        yml = yaml.safe_load(f.read())
    if not "consts" in yml:
        continue
    container_names[app_name] = list(
        [
            yml["consts"][k]
            for k in filter(
                lambda x: x.endswith("_container_name"), yml["consts"].keys()
            )
        ]
    )

for path in paths["questions"]:
    m = app_pat.search(path)
    train, app_name = m.groups()
    if app_name not in container_names:
        continue
    app_containers = container_names[app_name]
    with open(path, "r") as f:
        yml = yaml.safe_load(f.read())
    changed = False
    if not list(
        filter(lambda x: x["name"] == "Labels Configuration (Generated)", yml["groups"])
    ):
        yml["groups"].append(
            {
                "description": "Configure Labels (Generated)",
                "name": "Labels Configuration (Generated)",
            }
        )
        changed = True
    if not list(
        filter(
            lambda x: x["group"] == "Labels Configuration (Generated)", yml["questions"]
        )
    ):
        yml["questions"].append(
            {
                "group": "Labels Configuration (Generated)",
                "label": "",
                "schema": {
                    "default": [],
                    "items": [
                        {
                            "label": "Label",
                            "schema": {
                                "attrs": [
                                    {
                                        "label": "Key",
                                        "schema": {"required": True, "type": "string"},
                                        "variable": "key",
                                    },
                                    {
                                        "label": "Value",
                                        "schema": {"required": True, "type": "string"},
                                        "variable": "value",
                                    },
                                    {
                                        "description": "Containers "
                                        "where "
                                        "the "
                                        "label "
                                        "should "
                                        "be "
                                        "applied",
                                        "label": "Containers",
                                        "schema": {
                                            "items": [
                                                {
                                                    "label": "Container",
                                                    "schema": {
                                                        "enum": [
                                                            {
                                                                "description": x,
                                                                "value": x,
                                                            }
                                                            for x in app_containers
                                                        ],
                                                        "required": True,
                                                        "type": "string",
                                                    },
                                                    "variable": "container",
                                                }
                                            ],
                                            "type": "list",
                                        },
                                        "variable": "containers",
                                    },
                                ],
                                "type": "dict",
                            },
                            "variable": "label",
                        }
                    ],
                    "type": "list",
                },
                "variable": "labels",
            }
        )
        changed = True
    if changed:
        with open(path, "w") as f:
            yaml.dump(yml, f)
