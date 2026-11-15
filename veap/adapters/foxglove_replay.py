"""Export verified VEAP physics samples on their simulation-relative time axis."""
import argparse
import hashlib
import json
import os
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from veap.simulation.locked_replay import validate_execution
from veap.spec import load_scenario


def export(tape_path, trace_paths, output):
    import foxglove

    tape = json.loads(tape_path.read_bytes())
    scenario = load_scenario(tape["scenario_id"])
    context = foxglove.Context()
    topics = {}
    with TemporaryDirectory(dir=output.parent) as directory:
        temporary = Path(directory) / "replay.mcap"
        with foxglove.open_mcap(str(temporary), context=context):
            for path in trace_paths:
                source = path.read_bytes()
                trace = json.loads(source)["trace"]
                report = validate_execution(scenario, tape, trace)
                engine = report["engine"]
                topic = f"/veap/{engine}/physics"
                if topic in topics:
                    raise ValueError(f"duplicate engine topic {topic}")
                metadata = {
                    "tape_sha256": tape["tape_sha256"],
                    "source_file_sha256": hashlib.sha256(source).hexdigest(),
                    "clock": "simulation-relative nanoseconds from trace start",
                    "source_authenticity": "not_established",
                }
                channel = foxglove.Channel(topic, schema={"type": "object", "title": "VeapPhysicsSample",
                    "properties": {"tick": {"type": "integer"}, "time_s": {"type": "number"},
                                   "contacts": {"type": ["integer", "null"]},
                                   "position_xyz_m": {"type": "array", "items": {"type": "number"}}}},
                    metadata=metadata, context=context)
                for sample in trace["samples"]:
                    ns = round(Decimal(str(sample["time_s"])) * 1_000_000_000)
                    channel.log(sample, log_time=ns)
                topics[topic] = len(trace["samples"])
        # No overwrite, including when another export wins the race.
        os.link(temporary, output)
    return topics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tape", required=True, type=Path)
    parser.add_argument("--trace", required=True, type=Path, action="append")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(export(args.tape, args.trace, args.out)))


if __name__ == "__main__":
    main()
