import os
import sys
import subprocess
from datetime import datetime
import shutil


def archive_report(src_path: str, reports_dir: str = "reports"):
    """Move/copy pytest-generated report.html into reports/ with a timestamped filename and update an index."""
    if not os.path.exists(src_path):
        print(f"No report found at {src_path}; skipping archive.")
        return

    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_name = f"test_report_{timestamp}.html"
    dest_path = os.path.join(reports_dir, dest_name)

    # copy so original remains for any downstream tools
    shutil.copy2(src_path, dest_path)

    # also maintain a stable 'report.html' for quick access
    latest = os.path.join(reports_dir, "report.html")
    shutil.copy2(src_path, latest)

    # regenerate a simple index
    try:
        files = [n for n in os.listdir(reports_dir) if n.lower().endswith('.html')]
        files.sort(reverse=True)
        lines = ['<!doctype html>', '<html>', '<head><meta charset="utf-8"><title>Test Reports</title></head>', '<body>', '<h1>Available Test Reports</h1>', '<ul>']
        for fn in files:
            lines.append(f'<li><a href="{fn}">{fn}</a></li>')
        lines += ['</ul>', f'<p>Latest: <a href="{os.path.basename(latest)}">{os.path.basename(latest)}</a></p>', '</body>', '</html>']
        with open(os.path.join(reports_dir, 'index.html'), 'w', encoding='utf-8') as idx:
            idx.write('\n'.join(lines))
    except Exception as e:
        print(f"Failed to generate reports index: {e}")


if __name__ == "__main__":
    # Run pytest using the project's pytest.ini settings (pytest will pick addopts)
    print("Running pytest...")
    # Use the same Python executable to run pytest
    cmd = [sys.executable, '-m', 'pytest']

    # Allow optional parallelism via environment variable. By default we do NOT enable xdist to
    # prevent multiple webdriver instances opening when tests share a session-scoped driver.
    # Set PYTEST_WORKERS to 'auto' or a positive integer to enable -n.
    workers = os.environ.get('PYTEST_WORKERS', '').strip()
    if workers:
        # Validate workers value: allow 'auto' or a positive integer
        if workers.lower() == 'auto':
            cmd += ['-n', 'auto']
        else:
            try:
                w = int(workers)
                if w > 0:
                    cmd += ['-n', str(w)]
            except ValueError:
                print(f"Ignoring invalid PYTEST_WORKERS value: {workers}")
    try:
        print('Executing:', ' '.join(cmd))
        completed = subprocess.run(cmd, check=False)
    except Exception as e:
        print(f"Failed to run pytest: {e}")
        sys.exit(2)

    # Archive the html report if pytest-html produced report.html at project root
    archive_report('report.html')

    # Exit with pytest's exit code
    sys.exit(completed.returncode)
