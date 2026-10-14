#!/usr/bin/env python3
"""Check the outside-write check on this machine, with no agent: planted writes must be caught, an idle interval
must come back clean. It uses the real places (the system temp folder, C:\\tmp, the home folder, construction-eval/)
and removes everything it planted.

    bin/construction-python evals/harness/probe_leftovers.py [--idle SECONDS]

Planted, each from a shell command the way a run would issue it (the command check in guard.py sees none of the
Python ones): Python writing into Git Bash's /tmp and into C:\\tmp, Python writing through tempfile (the run's temp
folder), Python writing inside a folder that already exists (Documents/construction-eval-probe/nested/, which the
probe makes first and removes; it never writes into the user's own folders), and a shell redirect into /tmp. Exit 0
when every plant is caught and the idle interval is clean.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import leftovers  # noqa: E402
from guard import shell_write_targets  # noqa: E402
from runner import find_bash  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--idle", type=float, default=60, help="seconds of the idle control (default 60)")
    args = ap.parse_args()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    ws = Path(tempfile.gettempdir()) / "construction-eval" / f"probe-{stamp}-r1"
    run_tmp = leftovers.run_temp_for(ws)
    ws.mkdir(parents=True)
    run_tmp.mkdir()
    where = leftovers.places(ws, run_tmp)
    env = dict(os.environ, TMP=str(run_tmp), TEMP=str(run_tmp), TMPDIR=str(run_tmp))
    py = f'"{Path(sys.executable).as_posix()}"'
    c_tmp_existed = Path("C:/tmp").exists()
    name = f"planted-{stamp}"
    plants = {
        "python into Git Bash's /tmp": (f"{py} -c \"import subprocess; p = subprocess.run(['cygpath', '-w', '/tmp'], "
                                        f"capture_output=True, text=True).stdout.strip() or '/tmp'; "
                                        f"open(p + '/{name}-py.png', 'wb').write(b'x')\"", f"{name}-py.png"),
        "python into C:\\tmp": (f"{py} -c \"import os; os.makedirs('/tmp', exist_ok=True); "
                                f"open('/tmp/{name}-c.png', 'wb').write(b'x')\"", f"{name}-c.png"),
        "python through tempfile": (f"{py} -c \"import tempfile, os; "
                                    f"open(os.path.join(tempfile.gettempdir(), '{name}-tf.json'), 'w').write('x')\"",
                                    f"{name}-tf.json"),
        "shell redirect into /tmp": (f"echo x > /tmp/{name}-sh.txt", f"{name}-sh.txt"),
    }
    # Never into the user's own folders: the probe makes Documents/construction-eval-probe/nested/ before the
    # "run" starts, writes inside it as a run would write inside a folder that already exists, and removes it.
    docs = dict(leftovers.user_folders()).get("Documents")
    probe_dir = docs / "construction-eval-probe" if docs else None
    if probe_dir is not None and probe_dir.exists():
        print(f"{probe_dir} already exists: remove it (a probe left it) and run again; the probe writes only into a folder it made")
        shutil.rmtree(ws, ignore_errors=True)
        shutil.rmtree(run_tmp, ignore_errors=True)
        return 2
    doc_plant = None
    if probe_dir is not None:
        (probe_dir / "nested").mkdir(parents=True)
        doc_plant = probe_dir / "nested" / f"{name}-doc.png"
        plants["python inside a folder that already exists (Documents/construction-eval-probe/nested)"] = (
            f"{py} -c \"open(r'{doc_plant}', 'wb').write(b'x')\"", f"construction-eval-probe/nested/{doc_plant.name}")
    ok = True
    try:
        before, t0 = leftovers.snapshot(where), time.time() - leftovers.CLOCK_SLACK
        for label, (command, _) in plants.items():
            subprocess.run([find_bash(), "-c", command], cwd=ws, env=env, check=True, capture_output=True, timeout=60)
        hits = (leftovers.diff(where, before, leftovers.snapshot(where), own={ws.name, run_tmp.name})
                + leftovers.changed_since(leftovers.user_folders(), t0))
        for label, (command, file) in plants.items():
            found = [h for h in hits if h["name"] == file]
            seen_by_commands = bool(shell_write_targets(command, str(ws)))
            print(f"{'CAUGHT' if found else 'MISSED'} {label}: "
                  + (f"{found[0]['place']} {found[0]['path']}" if found else file)
                  + f" (command check: {'sees it' if seen_by_commands else 'misses it'})")
            ok &= bool(found)
        others = [h for h in hits if name not in h["name"] and h["name"] != "tmp"]
        if others:
            print("also new or changed during the plants:", [(h["place"], h["name"]) for h in others])
        print(f"idle control: {args.idle:.0f} s with nothing running in the probe ...", flush=True)
        before, t0 = leftovers.snapshot(where), time.time()
        time.sleep(args.idle)
        idle = (leftovers.diff(where, before, leftovers.snapshot(where), own={ws.name, run_tmp.name})
                + leftovers.changed_since(leftovers.user_folders(), t0))
        print("idle control: clean" if not idle else f"idle control: NOT clean: {[(h['place'], h['name'], h['change']) for h in idle]}")
        ok &= not idle
    finally:
        for p in (Path(tempfile.gettempdir()) / f"{name}-py.png", Path(tempfile.gettempdir()) / f"{name}-sh.txt",
                  Path("C:/tmp") / f"{name}-c.png"):
            p.unlink(missing_ok=True)
        if probe_dir is not None:
            shutil.rmtree(probe_dir, ignore_errors=True)
        if not c_tmp_existed and Path("C:/tmp").is_dir() and not any(Path("C:/tmp").iterdir()):
            Path("C:/tmp").rmdir()
        shutil.rmtree(ws, ignore_errors=True)
        shutil.rmtree(run_tmp, ignore_errors=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
