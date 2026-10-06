"""Deterministic invariants across small histories, beyond the named fixtures."""

from dataclasses import replace
from itertools import product

from openintuition_memory_check.policies import scoped_state
from openintuition_memory_check.schema import Event


def histories():
    actions = [('set', 'dark', None), ('set', 'light', None),
               ('temporary', 'dark', 'S1'), ('temporary', 'light', 'S2'),
               ('revoke', None, None), ('note', 'light', None)]
    for sequence in product(actions, repeat=3):
        yield tuple(Event(f'e{i}', i, op, 'theme', value, session)
                    for i, (op, value, session) in enumerate(sequence, 1))


def test_notes_and_unrelated_keys_cannot_change_answers():
    for events in histories():
        extra = (Event('unrelated', 4, 'revoke', 'language', None, None),
                 Event('note', 5, 'note', 'theme', 'dark', None))
        for session in ('S1', 'S2', 'S3'):
            assert scoped_state(events, 'theme', session) == scoped_state(events+extra, 'theme', session)


def test_global_reset_and_revoke_clear_every_session_exception():
    for events in histories():
        for session in ('S1', 'S2', 'S3'):
            assert scoped_state(events+(Event('reset', 4, 'set', 'theme', 'blue', None),), 'theme', session) == 'blue'
            assert scoped_state(events+(Event('forget', 4, 'revoke', 'theme', None, None),), 'theme', session) == 'ASK'


def test_session_renaming_preserves_behavior_and_other_sessions():
    for events in histories():
        renamed = tuple(replace(e, session_id='renamed' if e.session_id == 'S1' else e.session_id) for e in events)
        assert scoped_state(events, 'theme', 'S1') == scoped_state(renamed, 'theme', 'renamed')
        assert scoped_state(events, 'theme', 'S2') == scoped_state(renamed, 'theme', 'S2')
