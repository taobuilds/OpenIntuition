"""Self-contained browser reports; all dataset text stays inert."""

import base64
from dataclasses import asdict
from importlib.resources import files
import json

from .schema import Scenario


def report_payload(scenarios, predictions, summary, manifest):
    histories = {scenario.id: [asdict(event) for event in scenario.events] for scenario in scenarios}
    return {"summary": summary, "manifest": manifest, "predictions": [
        {**asdict(row), "events": [event for event in histories[row.scenario]
                                  if event["step"] <= row.as_of_step]}
        for row in predictions
    ]}


def html_report(scenarios: tuple[Scenario, ...], predictions, summary: dict, manifest: dict) -> str:
    resources = files("openintuition_memory_check").joinpath("resources")
    template = resources.joinpath("report.html").read_text(encoding="utf-8")
    payload = json.dumps(report_payload(scenarios, predictions, summary, manifest), ensure_ascii=False)
    # Even inside application/json, an HTML parser recognizes </script>.
    for character, escaped in (("&", "\\u0026"), ("<", "\\u003c"), (">", "\\u003e"),
                               ("\u2028", "\\u2028"), ("\u2029", "\\u2029")):
        payload = payload.replace(character, escaped)
    mascot = base64.b64encode(resources.joinpath("mascot.png").read_bytes()).decode("ascii")
    return template.replace("__MASCOT__", mascot).replace("__DATA__", payload)
