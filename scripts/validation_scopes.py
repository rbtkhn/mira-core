"""Explicit public-package coverage; full validation remains the default.

Corpus cases run in the separate, blocking corpus-integrity job. Nothing here
turns a corpus failure into success or supplies missing private source bytes.
"""
from __future__ import annotations

import json
from pathlib import Path

PUBLIC_CHECKS = frozenset({
    'model_substitution_gate_failures', 'skill_contract_failures',
    'archive.validate_repository_state',
    'tracked_artifact_failures', 'legacy_repository_identity_failures',
    'legacy_archive_name_failures', 'obsolete_guidance_failures',
})

CORPUS_CHECKS = frozenset({
    'archive_manifest_failures', 'daily_run_failures', 'forecast_ledger_failures',
    'markdown_link_failures', 'editorial_title_failures',
    'operational_claim_failures', 'verification_packet_failures',
    'reality_lattice_failures', 'voice_accountability_failures',
    'voice_judgment_failures', 'recursive_learning_ledger.validate_ledger',
    'mira_continuity.validate_control_plane_state',
    'mira_journal.validate_repository_state', 'archive_library.validate_scaffold',
    'operator_positions.validate_ledger', 'legacy_verification_inventory_failures',
    'voice_routing_failures',
})

# This module imports migration APIs for a corpus transaction not present in
# the published package, and its fixtures copy registered real Library notes.
CORPUS_MODULES = {
    'tests/test_library_note_relocation.py': 'registered Library notes and revision/approval corpus',
}
CORPUS_CASES = {
    'tests/test_freeman_historical_index.py::test_render_is_deterministic_and_contains_required_surfaces': 'Freeman occurrence ledger generated from hydrated source bodies',
    'tests/test_historical_reference_skill.py::test_explicit_voice_selection_and_stable_patterns': 'voice selection over the current manifest and existing transcript bodies',
    'tests/test_cross_voice_reference_density.py::test_report_contains_comparison_surfaces_and_is_deterministic': 'manifest-backed historical source bodies',
    'tests/test_library_integration.py::test_five_work_pilot_is_complete_without_essays': 'current registered Library notes, approvals and generated views; corpus-copy transaction',
    'tests/test_library_integration.py::test_human_views_are_deterministic_projections': 'current registered Library notes, approvals and generated views; corpus-copy transaction',
    'tests/test_library_integration.py::test_repository_reconciliation_does_not_write_when_current': 'current registered Library notes, approvals and generated views; corpus-copy transaction',
    'tests/test_library_integration.py::test_hard_reconciliation_writes_candidate_and_suspends_routes': 'current registered Library notes, approvals and generated views; corpus-copy transaction',
    'tests/test_library_integration.py::test_operational_route_index_exposes_only_the_digest_bound_reviewed_route': 'current registered Library notes, approvals and generated views; corpus-copy transaction',
    'tests/test_library_reasoning.py::test_cognitive_inventory_has_eight_current_heads_and_explicit_one_hop': 'current eight-work Library corpus and digest-bound route promotions',
    'tests/test_library_reasoning.py::test_negative_signature_cancels_promotion_and_prose_does_not_match': 'current eight-work Library corpus and digest-bound route promotions',
    'tests/test_voice_accountability_skill.py::test_july_known_explicit_admissions_are_retrieved': 'specific July source bodies and admission locations',
    'tests/test_voice_count_authority.py::test_voice_source_index_totals_match_the_manifest': 'current manifest and generated voice indexes',
    'tests/test_mira_continuity.py::test_current_mira_continuity_state_validates': 'generated private continuity views',
    'tests/test_reality.py::test_current_pilots_and_generated_views_validate': 'current reality/verification corpus',
    'tests/test_verification.py::test_registry_has_36_valid_sources_and_stable_read_only_payload': 'current verification source corpus',
}


def pytest_addoption(parser):
    parser.addoption('--public-package', action='store_true', help='Separate public controls from corpus checks')
    parser.addoption('--corpus-only', action='store_true', help='Run the explicitly assigned corpus tests')


def pytest_ignore_collect(collection_path, config):
    try:
        relative = collection_path.relative_to(config.rootpath).as_posix()
    except ValueError:
        return None
    if config.getoption('--public-package') and relative in CORPUS_MODULES:
        return True
    return None


def pytest_collection_modifyitems(config, items):
    public = config.getoption('--public-package')
    corpus = config.getoption('--corpus-only')
    if public and corpus:
        import pytest
        raise pytest.UsageError('public-package and corpus-only are mutually exclusive')
    if not public and not corpus:
        return
    selected, deferred = [], []
    for item in items:
        name = item.nodeid.split('[', 1)[0]
        is_corpus = name in CORPUS_CASES or item.nodeid.split('::')[0] in CORPUS_MODULES
        (selected if is_corpus == corpus else deferred).append(item)
    items[:] = selected
    config.hook.pytest_deselected(items=deferred)
    summary = {'scope': 'public-package' if public else 'corpus', 'selected_tests': len(selected),
               'deselected_tests': len(deferred),
               'corpus_test_nodes': [item.nodeid for item in (deferred if public else selected)],
               'corpus_modules': CORPUS_MODULES,
               'limits': 'Corpus checks are not passed or waived; see the separate corpus-integrity job.'}
    reporter = config.pluginmanager.get_plugin('terminalreporter')
    if reporter:
        reporter.write_line('validation_coverage ' + json.dumps(summary, sort_keys=True))


def checks_for_scope(checks, scope):
    if scope == 'all':
        return checks
    if scope not in {'public-package', 'corpus'}:
        raise ValueError('unknown validation scope: ' + scope)
    unknown = PUBLIC_CHECKS - {name for name, _ in checks}
    if unknown:
        raise ValueError('public checks missing: ' + ', '.join(sorted(unknown)))
    unclassified = {name for name, _ in checks} - PUBLIC_CHECKS - CORPUS_CHECKS
    if unclassified:
        raise ValueError('unclassified structural checks: ' + ', '.join(sorted(unclassified)))
    return tuple((name, check) for name, check in checks
                 if (name in PUBLIC_CHECKS) == (scope == 'public-package'))
