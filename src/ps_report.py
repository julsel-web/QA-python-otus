from __future__ import annotations

import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class ProcessInfo:
    user: str
    cpu_percent: float
    mem_percent: float
    command: str

    @property
    def process_name(self) -> str:
        return self.command[:20]


def run_ps_aux() -> str:
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def parse_percent(value: str) -> float:
    return float(value.replace(",", "."))


def parse_ps_aux(output: str) -> list[ProcessInfo]:
    lines = output.strip().splitlines()
    if len(lines) < 2:
        raise ValueError("Команда ps aux вернула недостаточно данных")

    processes: list[ProcessInfo] = []
    for line in lines[1:]:
        parts = line.split(None, 10)
        if len(parts) < 11:
            continue

        user, _, cpu, mem, *_rest, command = parts
        processes.append(
            ProcessInfo(
                user=user,
                cpu_percent=parse_percent(cpu),
                mem_percent=parse_percent(mem),
                command=command,
            )
        )

    return processes


def build_report(processes: list[ProcessInfo]) -> str:
    if not processes:
        raise ValueError("Не удалось распарсить процессы из ps aux")

    users = sorted({process.user for process in processes})
    process_counts = Counter(process.user for process in processes)
    total_cpu = sum(process.cpu_percent for process in processes)
    total_mem = sum(process.mem_percent for process in processes)
    top_cpu_process = max(processes, key=lambda process: process.cpu_percent)
    top_mem_process = max(processes, key=lambda process: process.mem_percent)

    report_lines = [
        "Отчёт о состоянии системы:",
        f"Пользователи системы: {', '.join(repr(user) for user in users)}",
        f"Процессов запущено: {len(processes)}",
        "",
        "Пользовательских процессов:",
    ]

    for user, count in sorted(process_counts.items()):
        report_lines.append(f"{user}: {count}")

    report_lines.extend(
        [
            f"Всего памяти используется: {total_mem:.1f}%",
            f"Всего CPU используется: {total_cpu:.1f}%",
            f"Больше всего памяти использует: {top_mem_process.process_name}",
            f"Больше всего CPU использует: {top_cpu_process.process_name}",
        ]
    )

    return "\n".join(report_lines)


def save_report(report: str, directory: Path | None = None) -> Path:
    target_directory = directory or Path.cwd()
    filename = datetime.now().strftime("%d-%m-%Y-%H:%M-scan.txt")
    report_path = target_directory / filename
    report_path.write_text(report, encoding="utf-8")
    return report_path


def main() -> None:
    output = run_ps_aux()
    processes = parse_ps_aux(output)
    report = build_report(processes)
    report_path = save_report(report)
    print(report)
    print()
    print(f"Отчёт сохранён в файл: {report_path}")


if __name__ == "__main__":
    main()
