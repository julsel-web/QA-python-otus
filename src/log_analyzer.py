from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from heapq import heappush, heappushpop
from pathlib import Path


LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ '
    r'\[(?P<timestamp>[^\]]+)\] '
    r'"(?P<request>.*)" '
    r'\d{3} \S+ '
    r'.* '
    r'(?P<duration>\d+)$'
)

SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD")


@dataclass(slots=True)
class RequestInfo:
    ip: str
    date: str
    method: str
    url: str
    duration: int


def parse_log_line(line: str) -> RequestInfo:
    match = LOG_PATTERN.match(line.strip())
    if not match:
        raise ValueError(f"Некорректная строка лога: {line.rstrip()}")

    request_parts = match.group("request").split()
    method = request_parts[0] if request_parts else "-"
    url = request_parts[1] if len(request_parts) > 1 else "-"

    return RequestInfo(
        ip=match.group("ip"),
        date=f'[{match.group("timestamp")}]',
        method=method,
        url=url,
        duration=int(match.group("duration")),
    )


def analyze_log_file(file_path: str | Path) -> dict:
    file_path = Path(file_path)
    total_requests = 0
    method_counts = Counter({method: 0 for method in SUPPORTED_METHODS})
    ip_counts = Counter()
    top_longest: list[tuple[int, int, RequestInfo]] = []

    with file_path.open(encoding="utf-8") as log_file:
        for line_number, line in enumerate(log_file):
            request = parse_log_line(line)
            total_requests += 1
            ip_counts[request.ip] += 1

            if request.method in method_counts:
                method_counts[request.method] += 1

            entry = (request.duration, -line_number, request)
            if len(top_longest) < 3:
                heappush(top_longest, entry)
            else:
                heappushpop(top_longest, entry)

    top_ips = dict(
        sorted(ip_counts.items(), key=lambda item: (-item[1], item[0]))[:3]
    )

    sorted_longest = sorted(top_longest, key=lambda item: (-item[0], -item[1]))
    longest_requests = [asdict(item[2]) for item in sorted_longest]

    return {
        "top_ips": top_ips,
        "top_longest": longest_requests,
        "total_stat": dict(method_counts),
        "total_requests": total_requests,
    }


def get_log_files(path: str | Path) -> list[Path]:
    path = Path(path)
    if path.is_file():
        return [path]

    if path.is_dir():
        return sorted(item for item in path.iterdir() if item.is_file())

    raise FileNotFoundError(f"Путь не найден: {path}")


def save_report(statistics: dict, source_file: str | Path, output_dir: str | Path) -> Path:
    source_file = Path(source_file)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{source_file.stem}_stats.json"
    with output_path.open("w", encoding="utf-8") as result_file:
        json.dump(statistics, result_file, indent=2, ensure_ascii=False)

    return output_path


def print_report(statistics: dict, source_file: str | Path, output_path: str | Path) -> None:
    print(f"Файл: {source_file}")
    print(f"JSON-отчёт: {output_path}")
    print(json.dumps(statistics, indent=2, ensure_ascii=False))
    print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Анализирует access.log и формирует JSON-отчёты со статистикой."
    )
    parser.add_argument(
        "path",
        help="Путь к лог-файлу или директории с логами.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="log_reports",
        help="Директория для сохранения JSON-отчётов. По умолчанию: log_reports",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    log_files = get_log_files(args.path)
    for log_file in log_files:
        statistics = analyze_log_file(log_file)
        output_path = save_report(statistics, log_file, args.output_dir)
        print_report(statistics, log_file, output_path)


if __name__ == "__main__":
    main()
