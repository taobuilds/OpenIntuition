"""Regenerate the checked-in demo from the packaged examples."""

from importlib.resources import as_file, files
from pathlib import Path

from openintuition_memory_check import __version__
from openintuition_memory_check.dataset import load_dataset
from openintuition_memory_check.evaluation import evaluate, markdown_report, summarize
from openintuition_memory_check.policies import POLICIES
from openintuition_memory_check.reporting import html_report

root = Path(__file__).resolve().parents[1]
with as_file(files('openintuition_memory_check').joinpath('resources', 'extended_scenarios.jsonl')) as path:
    dataset = load_dataset(path)
predictions = evaluate(dataset.scenarios, POLICIES)
summary = summarize(predictions)
manifest = {
    'report_schema_version': '0.1', 'tool_version': __version__,
    'dataset': {'name': dataset.name, 'sha256': dataset.sha256, 'size_bytes': dataset.size_bytes},
    'scenario_count': len(dataset.scenarios),
    'checkpoint_count': sum(len(s.checkpoints) for s in dataset.scenarios),
    'policies': list(POLICIES), 'metric': 'exact_match',
}
(root/'docs/index.html').write_text(html_report(dataset.scenarios, predictions, summary, manifest), encoding='utf-8')
(root/'docs/extended_results.md').write_text(markdown_report(predictions, summary), encoding='utf-8')
print('Updated docs/index.html and docs/extended_results.md from the extended suite.')
