"""Guard against false-positive RAGAS means after partial judge failures."""
import math

import pytest

from app.evaluators import _verified_ragas_frame


class Frame:
    def __init__(self, columns, n=None):
        self.data = columns
        self.columns = tuple(columns)
        self.n = n if n is not None else len(next(iter(columns.values())))

    def __len__(self):
        return self.n

    def __getitem__(self, column):
        return self.data[column]


GOOD = {
    "faithfulness": [0.9, 0.8],
    "answer_relevancy": [0.85, 0.95],
    "llm_context_precision_with_reference": [0.7, 0.6],
}


def test_complete_ragas_result_produces_full_coverage_means():
    out = _verified_ragas_frame(Frame(GOOD), 2)
    assert out["engine"] == "ragas"
    assert out["n"] == 2
    assert out["faithfulness"] == pytest.approx(0.85)
    assert out["answer_relevancy"] == pytest.approx(0.90)
    assert out["context_precision"] == pytest.approx(0.65)


def test_ragas_supported_column_aliases():
    table = {**GOOD}
    table["context_precision"] = table.pop("llm_context_precision_with_reference")
    table["response_relevancy"] = table.pop("answer_relevancy")
    assert _verified_ragas_frame(Frame(table), 2)["n"] == 2


@pytest.mark.parametrize("metric", list(GOOD))
@pytest.mark.parametrize("value", [float("nan"), float("inf"), None, True, "0.9", -0.1, 1.01])
def test_invalid_per_case_score_is_never_hidden_by_mean(metric, value):
    cols = {key: list(v) for key, v in GOOD.items()}
    cols[metric][0] = value
    with pytest.raises(RuntimeError, match="invalid or missing"):
        _verified_ragas_frame(Frame(cols), 2)


def test_no_missing_columns():
    cols = {key: list(v) for key, v in GOOD.items()}
    del cols["faithfulness"]
    with pytest.raises(RuntimeError, match="missing or ambiguous"):
        _verified_ragas_frame(Frame(cols), 2)


def test_no_partial_columns():
    cols = {key: list(v) for key, v in GOOD.items()}
    cols["faithfulness"] = [0.9]
    with pytest.raises(RuntimeError, match="incomplete"):
        _verified_ragas_frame(Frame(cols), 2)


def test_no_fewer_evaluated_rows_than_inputs():
    with pytest.raises(RuntimeError, match="incomplete evaluation rows"):
        _verified_ragas_frame(Frame(GOOD), 3)


def test_no_ambiguous_metric_column_names():
    cols = {key: list(v) for key, v in GOOD.items()}
    cols["context_precision"] = [0.9, 0.9]
    with pytest.raises(RuntimeError, match="ambiguous"):
        _verified_ragas_frame(Frame(cols), 2)


def test_empty_evaluation_is_invalid():
    with pytest.raises(RuntimeError, match="incomplete"):
        _verified_ragas_frame(Frame({"faithfulness": []}, n=0), 0)
