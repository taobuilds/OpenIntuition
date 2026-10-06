"""Reports preserve query boundaries, escape user text, and clean failed writes."""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest

from openintuition_memory_check.dataset import load_dataset, load_scenarios
from openintuition_memory_check.evaluation import evaluate, markdown_report, summarize, write_results
from openintuition_memory_check.policies import POLICIES
from openintuition_memory_check.reporting import html_report, report_payload

ROOT = Path(__file__).resolve().parents[1]


def inputs():
    dataset = load_dataset(ROOT / 'data/extended_scenarios.jsonl')
    predictions = evaluate(dataset.scenarios, POLICIES)
    manifest = {'tool_version': 'test', 'dataset': {'name': dataset.name, 'sha256': dataset.sha256}}
    return dataset.scenarios, predictions, summarize(predictions), manifest


def test_extended_labels_and_category_balance():
    scenarios, predictions, summary, manifest = inputs()
    assert len(scenarios) == 20
    assert sum(len(s.checkpoints) for s in scenarios) == 72
    assert all(sum(s.category == category for s in scenarios) == 5
               for category in ('update', 'temporary', 'revoke', 'distractor'))
    assert summary['scoped_state']['correct'] == 72
    assert summary['naive_last_value']['correct'] == 54
    assert summary['naive_last_value']['scenarios_passed'] == 10
    assert manifest['dataset']['sha256'] == hashlib.sha256((ROOT/'data/extended_scenarios.jsonl').read_bytes()).hexdigest()
    assert (ROOT/'data/extended_scenarios.jsonl').read_bytes() == (ROOT/'src/openintuition_memory_check/resources/extended_scenarios.jsonl').read_bytes()


def test_report_payload_never_displays_future_events():
    scenarios, predictions, summary, manifest = inputs()
    payload = report_payload(scenarios, predictions, summary, manifest)
    for row in payload['predictions']:
        assert len(row['events']) == row['as_of_step']
        assert all(event['step'] <= row['as_of_step'] for event in row['events'])
        assert all('expected' not in event for event in row['events'])


def test_html_text_cannot_close_script_or_create_markup():
    scenarios, _, _, manifest = inputs()
    hostile = '</script><script>window.injected=true</script><img src=x onerror=alert(1)>\u2028&'
    original = scenarios[0]
    modified = replace(original, events=tuple(replace(e, value=hostile) if e.op == 'set' else e for e in original.events),
                       checkpoints=tuple(replace(c, expected=hostile) for c in original.checkpoints))
    predictions = evaluate((modified,), POLICIES)
    html = html_report((modified,), predictions, summarize(predictions), manifest)
    assert hostile not in html
    embedded = re.search(r'<script type="application/json" id="report-data">(.*?)</script>', html, re.S).group(1)
    assert '<' not in embedded
    payload = json.loads(embedded)
    assert payload['predictions'][0]['predicted'] == hostile
    assert 'textContent' in html
    assert 'innerHTML' not in html
    mismatched = tuple(replace(row, expected='different', correct=False) for row in predictions)
    markdown = markdown_report(mismatched, summarize(mismatched))
    assert hostile not in markdown
    assert '&lt;script&gt;' in markdown


def test_failed_output_write_leaves_no_partial_directory(tmp_path, monkeypatch):
    scenarios, predictions, summary, manifest = inputs()
    original = Path.open

    def fail_on_predictions(path, *args, **kwargs):
        if path.name == 'predictions.jsonl' and args and args[0] == 'x':
            raise OSError('simulated disk error')
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'open', fail_on_predictions)
    output = tmp_path / 'broken'
    with pytest.raises(OSError, match='simulated disk error'):
        write_results(output, predictions, summary, scenarios=scenarios, manifest=manifest)
    assert not output.exists()


def test_runs_are_deterministic_and_manifest_matches_input(tmp_path):
    command = [sys.executable, '-m', 'openintuition_memory_check', 'demo', '--output']
    first, second = tmp_path/'first', tmp_path/'second'
    for path in (first, second):
        result = subprocess.run(command+[str(path)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    assert {p.name for p in first.iterdir()} == {'report.md', 'report.html', 'predictions.jsonl', 'summary.json', 'manifest.json'}
    assert all(path.read_bytes() == (second/path.name).read_bytes() for path in first.iterdir())
    manifest = json.loads((first/'manifest.json').read_text())
    assert manifest['scenario_count'] == 20
    assert manifest['checkpoint_count'] == 72
    assert manifest['dataset']['sha256'] == load_dataset(ROOT/'data/extended_scenarios.jsonl').sha256


def test_raw_unicode_line_separator_remains_inside_json_string(tmp_path):
    path = tmp_path/'unicode.jsonl'
    raw = (ROOT/'data/scenarios.jsonl').read_text().splitlines()[0]
    data = json.loads(raw)
    data['events'][0]['value'] = 'dark\u2028mode'
    path.write_text(json.dumps(data, ensure_ascii=False)+'\n')
    assert load_scenarios(path)[0].events[0].value == 'dark\u2028mode'


@pytest.mark.parametrize('policy,exit_code', [('naive_last_value', 1), ('scoped_state', 0)])
def test_strict_exit_code_supports_regression_checks(tmp_path, policy, exit_code):
    output = tmp_path/'strict'
    result = subprocess.run([
        sys.executable, '-m', 'openintuition_memory_check', 'run',
        '--data', str(ROOT/'data/extended_scenarios.jsonl'), '--policy', policy,
        '--output', str(output), '--fail-on-mismatch',
    ], capture_output=True, text=True)
    assert result.returncode == exit_code, result.stderr
    assert (output/'report.html').exists()
