import json
import sys
from pathlib import Path


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def save_json(path: Path, data) -> None:
    with path.open("w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def build_value_mapping(annotations: dict[str, str]) -> list[dict]:
    options = {}
    for index, ip in enumerate(sorted(annotations)):
        note = annotations[ip].strip()
        display = ip if not note else f"{ip}（{note}）"
        options[ip] = {
            "index": index,
            "text": display,
        }
    return [
        {
            "type": "value",
            "options": options,
        }
    ]


def update_dashboard(dashboard: dict, annotations: dict[str, str]) -> None:
    panel = next(
        (panel for panel in dashboard.get("panels", []) if panel.get("title") == "主な送信元 IP"),
        None,
    )
    if panel is None:
        raise ValueError("target panel not found: 主な送信元 IP")

    overrides = panel.setdefault("fieldConfig", {}).setdefault("overrides", [])
    target_override = None
    for override in overrides:
        matcher = override.get("matcher", {})
        if matcher.get("id") == "byName" and matcher.get("options") == "送信元 IP":
            target_override = override
            break

    if target_override is None:
        raise ValueError("送信元 IP override not found")

    properties = target_override.setdefault("properties", [])
    mapping_property = None
    for prop in properties:
        if prop.get("id") == "mappings":
            mapping_property = prop
            break

    if mapping_property is None:
        properties.append(
            {
                "id": "mappings",
                "value": build_value_mapping(annotations),
            }
        )
    else:
        mapping_property["value"] = build_value_mapping(annotations)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: update_grafana_annotations.py ANNOTATIONS_JSON DASHBOARD_JSON", file=sys.stderr)
        return 1

    annotations_path = Path(sys.argv[1])
    dashboard_path = Path(sys.argv[2])

    annotations_doc = load_json(annotations_path)
    dashboard_doc = load_json(dashboard_path)
    annotations = annotations_doc.get("source_ip_annotations", {})
    if not isinstance(annotations, dict):
        raise ValueError("source_ip_annotations must be an object")

    update_dashboard(dashboard_doc, annotations)
    save_json(dashboard_path, dashboard_doc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
