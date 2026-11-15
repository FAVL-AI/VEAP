"""Read project-scoped Foxglove v1 recording metadata. No credential persistence."""
import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


def zulu(value):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?Z", value):
        raise ValueError("expected an RFC3339 UTC timestamp with up to nine fractional digits")
    datetime.fromisoformat(value)
    return value


def recordings(session, project, token, *, limit=2000, start=None, end=None, sleep=time.sleep):
    if not project or not token or not 1 <= limit <= 2000:
        raise ValueError("project, credential and limit in 1..2000 are required")
    params = {"projectId": project, "limit": limit, "offset": 0,
              "sortBy": "start", "sortOrder": "asc"}
    for key, value in (("start", start), ("end", end)):
        if value is not None:
            params[key] = zulu(value)
    while True:
        for attempt in range(4):
            response = session.get("https://api.foxglove.dev/v1/recordings", params=params.copy(),
                                   headers={"Authorization": f"Bearer {token}"},
                                   allow_redirects=False, timeout=(5, 30))
            if response.status_code != 429 or attempt == 3:
                break
            retry = response.headers.get("Retry-After")
            delay = 2 ** attempt
            if retry:
                try:
                    delay = int(retry)
                except ValueError:
                    delay = (parsedate_to_datetime(retry) - datetime.now(timezone.utc)).total_seconds()
            if delay > 120:
                raise RuntimeError("rate limit requires a later retry")
            sleep(max(0, delay))
        if response.status_code != 200:
            raise RuntimeError(f"Foxglove recordings returned HTTP {response.status_code}")
        rows = response.json()
        if not isinstance(rows, list) or len(rows) > limit:
            raise ValueError("unexpected recordings page")
        yield from rows
        if len(rows) < limit:
            return
        params["offset"] += len(rows)


def main():
    import requests
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--limit", type=int, default=2000, help="page size")
    parser.add_argument("--start", type=zulu)
    parser.add_argument("--end", type=zulu)
    args = parser.parse_args()
    with requests.Session() as session:
        for row in recordings(session, args.project, os.getenv("FOXGLOVE_TOKEN"), limit=args.limit,
                              start=args.start, end=args.end):
            print(json.dumps(row))


if __name__ == "__main__":
    main()
