import json

import pytest

from scripts.check_consultation_quotes import check_quotes, main


def source():
    return [{"id": "S01", "path": "private", "paragraphs": [
        {"id": "S01-P001", "text": "We uh might reduce costs, if demand falls."},
        {"id": "S01-P002", "text": "A separate argument."}]}]


@pytest.mark.parametrize("pid,quote,status", [
    ("S01-P001", "might reduce costs, if", "passed"),
    ("S01-P001", "We might reduce costs", "quotation mismatch"),
    ("S01-P001", "costs if", "quotation mismatch"),
    ("S01-P001", "Might reduce", "quotation mismatch"),
    ("S01-P002", "might reduce costs", "quotation mismatch"),
    ("absent", "might reduce costs", "missing paragraph"),
])
def test_literal_match(pid, quote, status):
    result = check_quotes(source(), [{"paragraph_id": pid, "quotation": quote}])
    assert result["results"][0]["status"] == status


@pytest.mark.parametrize("quotes", [None, [], [None], [{}],
    [{"paragraph_id": "S01-P001", "quotation": " "}],
    [{"paragraph_id": 2, "quotation": "words"}]])
def test_invalid_quotes(quotes):
    assert check_quotes(source(), quotes)["status"] == "invalid input"


@pytest.mark.parametrize("index", [None, [], [None], [{}],
    [{"id": "S", "paragraphs": [None]}],
    [{"id": "S", "paragraphs": [{"id": "P", "text": 3}]}]])
def test_invalid_index(index):
    assert check_quotes(index, [{"paragraph_id": "P", "quotation": "x"}])["status"] == "invalid input"


def test_duplicate_ids_across_sources():
    index = source()
    index.append({"id": "S02", "paragraphs": index[0]["paragraphs"]})
    assert check_quotes(index, [{"paragraph_id": "S01-P001", "quotation": "We"}])["status"] == "invalid input"


@pytest.mark.parametrize("quote,expected", [("might", 0), ("never", 1), ("", 2)])
def test_cli_read_only_and_private(tmp_path, capsys, quote, expected):
    index, quotes = tmp_path / "index.json", tmp_path / "quotes.json"
    index.write_text(json.dumps(source()), encoding="utf-8")
    quotes.write_text(json.dumps([{"paragraph_id": "S01-P001", "quotation": quote}]), encoding="utf-8")
    before = (index.read_bytes(), quotes.read_bytes())
    assert main(["--index", str(index), "--quotes", str(quotes)]) == expected
    output = capsys.readouterr().out
    assert "We uh" not in output and "private" not in output
    assert before == (index.read_bytes(), quotes.read_bytes())
    assert len(list(tmp_path.iterdir())) == 2


def test_bad_json(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text('{"secret":broken', encoding="utf-8")
    assert main(["--index", str(bad), "--quotes", str(bad)]) == 2
    output = capsys.readouterr().out
    assert "invalid input" in output and "secret" not in output
