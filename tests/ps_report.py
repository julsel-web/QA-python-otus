import argparse
import curses
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


DEFAULT_TIMEOUT = 300
GRACEFUL_SHUTDOWN_SECONDS = 5


def build_parser():
    parser = argparse.ArgumentParser(
        prog="qa-snapshot",
        description="Утилита для сохранения snapshot окружения и запуска pytest.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser(
        "snapshot",
        help="Сохранить информацию о системе в JSON.",
    )
    snapshot_parser.add_argument(
        "-o",
        "--output",
        default="snapshot.json",
        help="Путь к выходному JSON-файлу.",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Запустить pytest для указанного теста с таймаутом.",
    )
    run_parser.add_argument(
        "test",
        help="Цель pytest, например tests/test_sample.py",
    )
    run_parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Таймаут в секундах. По умолчанию: {DEFAULT_TIMEOUT}",
    )

    watch_parser = subparsers.add_parser(
        "watch",
        help="Запустить pytest и показать TUI с CPU/RAM/FD.",
    )
    watch_parser.add_argument(
        "test",
        help="Цель pytest, например tests/test_sample.py",
    )
    watch_parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Таймаут в секундах. По умолчанию: {DEFAULT_TIMEOUT}",
    )
    watch_parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Интервал обновления экрана в секундах. По умолчанию: 0.5",
    )

    return parser


def get_rlimit(name):
    limit_name = getattr(resource, name, None)
    if limit_name is None:
        return None

    soft, hard = resource.getrlimit(limit_name)
    return {
        "soft": soft,
        "hard": hard,
    }


def collect_resources():
    limits = {
        "RLIMIT_NOFILE": get_rlimit("RLIMIT_NOFILE"),
        "RLIMIT_CPU": get_rlimit("RLIMIT_CPU"),
        "RLIMIT_AS": get_rlimit("RLIMIT_AS"),
    }

    return {
        "cpu_count": os.cpu_count(),
        "loadavg": os.getloadavg() if hasattr(os, "getloadavg") else None,
        "pagesize": resource.getpagesize(),
        "limits": limits,
    }


def collect_snapshot():
    return {
        "timestamp": datetime.now().isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "python_executable": sys.executable,
        },
        "environment": dict(os.environ),
        "resources": collect_resources(),
    }


def save_snapshot(output_path):
    snapshot = collect_snapshot()
    path = Path(output_path)
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def build_pytest_command(test_target):
    return [sys.executable, "-m", "pytest", test_target]


def terminate_process(process):
    if process.poll() is not None:
        return

    process.terminate()

    try:
        process.wait(timeout=GRACEFUL_SHUTDOWN_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def run_pytest(test_target, timeout):
    command = build_pytest_command(test_target)
    process = subprocess.Popen(command)

    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        terminate_process(process)
        return 124
    except KeyboardInterrupt:
        terminate_process(process)
        return 130


def read_proc_stat(pid):
    stat_path = Path(f"/proc/{pid}/stat")
    content = stat_path.read_text(encoding="utf-8")
    parts = content.split()

    return {
        "utime": int(parts[13]),
        "stime": int(parts[14]),
        "rss_pages": int(parts[23]),
    }


def read_proc_status_name(pid):
    status_path = Path(f"/proc/{pid}/status")
    for line in status_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Name:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def read_fd_count(pid):
    fd_path = Path(f"/proc/{pid}/fd")
    return len(list(fd_path.iterdir()))


def collect_process_metrics(pid, previous_total_cpu_time, previous_timestamp):
    now = time.time()
    stat = read_proc_stat(pid)
    ticks_per_second = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
    page_size = os.sysconf("SC_PAGE_SIZE")

    total_cpu_time = (stat["utime"] + stat["stime"]) / ticks_per_second
    ram_bytes = stat["rss_pages"] * page_size
    fd_count = read_fd_count(pid)

    cpu_percent = 0.0
    if previous_total_cpu_time is not None and previous_timestamp is not None:
        elapsed_cpu = total_cpu_time - previous_total_cpu_time
        elapsed_time = now - previous_timestamp
        if elapsed_time > 0:
            cpu_percent = (elapsed_cpu / elapsed_time) * 100

    return {
        "name": read_proc_status_name(pid),
        "cpu_percent": cpu_percent,
        "ram_mb": ram_bytes / (1024 * 1024),
        "fd_count": fd_count,
        "total_cpu_time": total_cpu_time,
        "timestamp": now,
    }


def draw_screen(stdscr, test_target, pid, timeout, start_time, metrics, exit_code):
    stdscr.erase()
    stdscr.addstr(0, 0, "qa-snapshot watch")
    stdscr.addstr(1, 0, f"Тест: {test_target}")
    stdscr.addstr(2, 0, f"PID: {pid}")
    stdscr.addstr(3, 0, f"Таймаут: {timeout}с")
    stdscr.addstr(4, 0, f"Прошло времени: {time.time() - start_time:.1f}с")

    if metrics is not None:
        stdscr.addstr(6, 0, f"Имя процесса: {metrics['name']}")
        stdscr.addstr(7, 0, f"CPU: {metrics['cpu_percent']:.1f}%")
        stdscr.addstr(8, 0, f"RAM: {metrics['ram_mb']:.1f} MB")
        stdscr.addstr(9, 0, f"FD: {metrics['fd_count']}")

    if exit_code is None:
        stdscr.addstr(11, 0, "Статус: выполняется")
        stdscr.addstr(12, 0, "Нажми q, чтобы остановить тест")
    else:
        stdscr.addstr(11, 0, f"Статус: завершён с кодом {exit_code}")
        stdscr.addstr(12, 0, "Нажми любую клавишу для выхода")

    stdscr.refresh()


def watch_pytest(stdscr, test_target, timeout, interval):
    curses.curs_set(0)
    stdscr.nodelay(True)

    command = build_pytest_command(test_target)
    process = subprocess.Popen(command)
    start_time = time.time()
    previous_total_cpu_time = None
    previous_timestamp = None
    exit_code = None

    try:
        while True:
            if process.poll() is not None:
                exit_code = process.returncode

            metrics = None
            if exit_code is None:
                try:
                    metrics = collect_process_metrics(
                        process.pid,
                        previous_total_cpu_time,
                        previous_timestamp,
                    )
                    previous_total_cpu_time = metrics["total_cpu_time"]
                    previous_timestamp = metrics["timestamp"]
                except FileNotFoundError:
                    exit_code = process.poll()

            draw_screen(
                stdscr,
                test_target,
                process.pid,
                timeout,
                start_time,
                metrics,
                exit_code,
            )

            key = stdscr.getch()
            if key == ord("q") and exit_code is None:
                terminate_process(process)
                exit_code = process.returncode

            if exit_code is not None:
                stdscr.nodelay(False)
                stdscr.getch()
                return exit_code

            if time.time() - start_time > timeout:
                terminate_process(process)
                return 124

            time.sleep(interval)
    except KeyboardInterrupt:
        terminate_process(process)
        return 130


def run_watch(test_target, timeout, interval):
    return curses.wrapper(watch_pytest, test_target, timeout, interval)


def handle_snapshot(args):
    path = save_snapshot(args.output)
    print(f"Snapshot сохранён в файл: {path}")


def handle_run(args):
    exit_code = run_pytest(args.test, args.timeout)
    raise SystemExit(exit_code)


def handle_watch(args):
    exit_code = run_watch(args.test, args.timeout, args.interval)
    raise SystemExit(exit_code)


def main():
    parser = build_parser()
    args = parser.parse_args()

    handlers = {
        "snapshot": handle_snapshot,
        "run": handle_run,
        "watch": handle_watch,
    }

    handlers[args.command](args)


if __name__ == "__main__":
    main()