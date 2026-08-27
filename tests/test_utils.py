from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cloudsecurity_af.agents._utils import extract_harness_result
from cloudsecurity_af.schemas.hunt import HuntResult


class TestExtractHarnessResult:
    def test_parsed_is_correct_type(self) -> None:
        expected = HuntResult(findings=[], total_raw=0)
        mock_result = MagicMock()
        mock_result.is_error = False
        mock_result.parsed = expected
        assert extract_harness_result(mock_result, HuntResult, "test") is expected

    def test_parsed_is_dict_validates(self) -> None:
        mock_result = MagicMock()
        mock_result.is_error = False
        mock_result.parsed = {"findings": [], "total_raw": 5}
        result = extract_harness_result(mock_result, HuntResult, "test")
        assert isinstance(result, HuntResult)
        assert result.total_raw == 5

    def test_error_raises(self) -> None:
        mock_result = MagicMock()
        mock_result.is_error = True
        mock_result.error_message = "something broke"
        mock_result.result = None
        mock_result.num_turns = 3
        mock_result.duration_ms = 1000
        with pytest.raises(RuntimeError, match="test harness error"):
            extract_harness_result(mock_result, HuntResult, "test")

    def test_invalid_parsed_raises_type_error(self) -> None:
        mock_result = MagicMock()
        mock_result.is_error = False
        mock_result.parsed = "not a dict or HuntResult"
        with pytest.raises(TypeError, match="did not return a valid"):
            extract_harness_result(mock_result, HuntResult, "test")
