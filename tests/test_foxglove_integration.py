import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from veap.adapters.foxglove_recordings import recordings, zulu
from veap.adapters.foxglove_replay import export

DATA = Path(__file__).resolve().parents[1] / "artifacts/research"


def test_retained_traces_roundtrip(tmp_path):
    pytest.importorskip("foxglove")
    from mcap.reader import make_reader
    tape = DATA / "v06-control-tape.json"
    paths = [DATA / f"v06-{engine}-locked-replay.json" for engine in ("mujoco", "isaaclab")]
    output = tmp_path / "replay.mcap"
    export(tape, paths, output)
    seen = {}
    with output.open("rb") as f:
        for schema, channel, message in make_reader(f).iter_messages():
            assert channel.metadata["tape_sha256"] == json.loads(tape.read_bytes())["tape_sha256"]
            sample = json.loads(message.data)
            assert message.log_time == round(sample["time_s"] * 1e9)
            seen.setdefault(channel.topic, []).append(sample)
    for path in paths:
        trace = json.loads(path.read_bytes())["trace"]
        assert seen["/veap/" + trace["manifest"]["engine"] + "/physics"] == trace["samples"]
    with pytest.raises(FileExistsError):
        export(tape, paths, output)
    with pytest.raises(ValueError, match="duplicate"):
        export(tape, paths * 2, tmp_path / "invalid.mcap")
    assert not (tmp_path / "invalid.mcap").exists()


def test_pages_and_backoff():
    session = Mock()
    wait = Mock()
    session.get.side_effect = [
        Mock(status_code=429, headers={"Retry-After": "4"}),
        Mock(status_code=200, json=lambda: [{"id": "a"}]),
        Mock(status_code=200, json=lambda: []),
    ]
    start = "2023-04-06T18:27:45.876543210Z"
    assert list(recordings(session, "project", "test", limit=1, start=start, sleep=wait)) == [{"id": "a"}]
    wait.assert_called_once_with(4)
    calls = [call.kwargs["params"] for call in session.get.call_args_list]
    assert [p["offset"] for p in calls] == [0, 0, 1]
    assert all(p["projectId"] == "project" and p["start"] == start for p in calls)


def test_access_denied_and_invalid_inputs():
    session = Mock()
    session.get.return_value = Mock(status_code=403)
    with pytest.raises(RuntimeError, match="403"):
        list(recordings(session, "p", "test"))
    assert session.get.call_count == 1
    with pytest.raises(ValueError):
        list(recordings(session, "p", "test", limit=2001))
    with pytest.raises(ValueError):
        zulu("2023-04-06T09:15:30+01:00")
