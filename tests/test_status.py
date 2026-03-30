"""Tests for yojenkins/yo_jenkins/status.py"""

import pytest

from yojenkins.yo_jenkins.status import BuildStatus, Color, Sound, StageStatus, Status


class TestStatusEnum:
    """Tests for the Status enum which holds lists of equivalent status strings."""

    def test_status_running_values(self):
        assert Status.RUNNING.value == ['RUNNING', 'IN_PROGRESS']

    def test_status_success_values(self):
        assert Status.SUCCESS.value == ['SUCCESS', 'SUCCEEDED']

    def test_status_failure_values(self):
        assert Status.FAILURE.value == ['FAILURE', 'FAILED', 'FAIL']

    def test_status_queued_value(self):
        assert Status.QUEUED.value == ['QUEUED']

    def test_status_aborted_value(self):
        assert Status.ABORTED.value == ['ABORTED']

    def test_status_unstable_value(self):
        assert Status.UNSTABLE.value == ['UNSTABLE']

    def test_status_paused_input_value(self):
        assert Status.PAUSED_INPUT.value == ['PAUSED_PENDING_INPUT']

    def test_status_not_found_value(self):
        assert Status.NOT_FOUND.value == ['NOT FOUND OR STARTED']

    def test_status_not_run_values(self):
        assert Status.NOT_RUN.value == ['NOT_EXECUTED', 'NOT_RUN']

    def test_status_none_value(self):
        assert Status.NONE.value == [None]

    def test_status_unknown_value(self):
        assert Status.UNKNOWN.value == ['UNKNOWN']

    def test_status_has_all_expected_members(self):
        expected = {
            'RUNNING', 'SUCCESS', 'FAILURE', 'QUEUED', 'ABORTED',
            'UNSTABLE', 'PAUSED_INPUT', 'NOT_FOUND', 'NOT_RUN', 'NONE', 'UNKNOWN',
        }
        assert set(Status.__members__.keys()) == expected

    @pytest.mark.parametrize(
        'status_text,expected_member',
        [
            ('RUNNING', Status.RUNNING),
            ('IN_PROGRESS', Status.RUNNING),
            ('SUCCEEDED', Status.SUCCESS),
            ('FAILED', Status.FAILURE),
            ('FAIL', Status.FAILURE),
        ],
    )
    def test_status_membership_lookup(self, status_text, expected_member):
        """Verify that alternate status text strings map back to the correct enum member."""
        assert status_text in expected_member.value


class TestBuildStatusEnum:
    """Tests for BuildStatus which picks the first element from each Status list."""

    @pytest.mark.parametrize(
        'member_name,expected_value',
        [
            ('RUNNING', 'RUNNING'),
            ('SUCCESS', 'SUCCESS'),
            ('FAILURE', 'FAILURE'),
            ('QUEUED', 'QUEUED'),
            ('ABORTED', 'ABORTED'),
            ('UNSTABLE', 'UNSTABLE'),
            ('PAUSED_INPUT', 'PAUSED_PENDING_INPUT'),
            ('NOT_FOUND', 'NOT FOUND OR STARTED'),
            ('NOT_RUN', 'NOT_EXECUTED'),
            ('UNKNOWN', 'UNKNOWN'),
        ],
    )
    def test_build_status_value(self, member_name, expected_value):
        assert BuildStatus[member_name].value == expected_value

    def test_build_status_none_is_none(self):
        assert BuildStatus.NONE.value is None

    def test_build_status_derives_from_status_index_zero(self):
        """Every BuildStatus value should equal Status[same_name].value[0]."""
        for member in BuildStatus:
            assert member.value == Status[member.name].value[0]


class TestStageStatusEnum:
    """Tests for StageStatus which differs from BuildStatus only for RUNNING."""

    def test_stage_status_running_uses_in_progress(self):
        """StageStatus.RUNNING uses index 1 (IN_PROGRESS) instead of index 0."""
        assert StageStatus.RUNNING.value == 'IN_PROGRESS'

    def test_stage_status_running_differs_from_build_status(self):
        assert StageStatus.RUNNING.value != BuildStatus.RUNNING.value

    @pytest.mark.parametrize(
        'member_name',
        ['SUCCESS', 'FAILURE', 'QUEUED', 'ABORTED', 'UNSTABLE', 'PAUSED_INPUT', 'NOT_FOUND', 'NOT_RUN', 'UNKNOWN'],
    )
    def test_stage_status_non_running_matches_build_status(self, member_name):
        """All non-RUNNING members should match BuildStatus values."""
        assert StageStatus[member_name].value == BuildStatus[member_name].value

    def test_stage_status_none_is_none(self):
        assert StageStatus.NONE.value is None


class TestColorEnum:
    """Tests for the Color enum which maps status names to color strings."""

    def test_color_items_has_all_status_keys(self):
        expected_keys = {
            'RUNNING', 'SUCCESS', 'FAILURE', 'QUEUED', 'ABORTED',
            'UNSTABLE', 'PAUSED_INPUT', 'NOT_FOUND', 'NOT_RUN', 'NONE', 'UNKNOWN',
        }
        assert set(Color.ITEMS.value.keys()) == expected_keys

    @pytest.mark.parametrize(
        'status_key,expected_color',
        [
            ('SUCCESS', 'green'),
            ('FAILURE', 'red'),
            ('ABORTED', 'magenta'),
            ('UNSTABLE', 'orange'),
            ('PAUSED_INPUT', 'cyan'),
            ('NOT_RUN', 'grey-dark'),
        ],
    )
    def test_color_specific_mappings(self, status_key, expected_color):
        assert Color.ITEMS.value[status_key] == expected_color

    @pytest.mark.parametrize(
        'status_key',
        ['RUNNING', 'QUEUED', 'NOT_FOUND', 'NONE', 'UNKNOWN'],
    )
    def test_color_normal_defaults(self, status_key):
        assert Color.ITEMS.value[status_key] == 'normal'


class TestSoundEnum:
    """Tests for the Sound enum which maps status names to sound filenames."""

    def test_sound_items_has_all_status_keys(self):
        expected_keys = {
            'RUNNING', 'SUCCESS', 'FAILURE', 'QUEUED', 'ABORTED',
            'UNSTABLE', 'PAUSED_INPUT', 'NOT_FOUND', 'NOT_RUN', 'NONE', 'UNKNOWN',
        }
        assert set(Sound.ITEMS.value.keys()) == expected_keys

    @pytest.mark.parametrize(
        'status_key',
        ['SUCCESS', 'FAILURE', 'ABORTED', 'UNSTABLE', 'PAUSED_INPUT'],
    )
    def test_sound_has_wav_file_for_actionable_statuses(self, status_key):
        value = Sound.ITEMS.value[status_key]
        assert value.endswith('.wav'), f'Expected .wav file for {status_key}, got: {value!r}'

    @pytest.mark.parametrize(
        'status_key',
        ['RUNNING', 'QUEUED', 'NOT_FOUND', 'NOT_RUN', 'NONE', 'UNKNOWN'],
    )
    def test_sound_empty_for_non_actionable_statuses(self, status_key):
        assert Sound.ITEMS.value[status_key] == ''
