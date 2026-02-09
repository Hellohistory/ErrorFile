import argparse
import statistics
import sys
import tempfile
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ErrorFile import inspect_files
from PIL import Image
from PyPDF2 import PdfWriter


def _create_good_png(path: Path) -> None:
    image = Image.new("RGB", (32, 32), color="blue")
    image.save(path, format="PNG")


def _create_good_pdf(path: Path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(path, "wb") as pdf_file:
        writer.write(pdf_file)


def build_dataset(base_dir: Path, samples: int, bad_ratio: float) -> list[str]:
    png_good = base_dir / "seed_good.png"
    pdf_good = base_dir / "seed_good.pdf"
    _create_good_png(png_good)
    _create_good_pdf(pdf_good)
    png_good_bytes = png_good.read_bytes()
    pdf_good_bytes = pdf_good.read_bytes()

    paths: list[str] = []
    bad_count = int(samples * bad_ratio)
    for index in range(samples):
        is_bad = index < bad_count
        is_png = index % 2 == 0
        if is_png:
            path = base_dir / f"sample_{index:05d}.png"
            payload = b"not-a-png" if is_bad else png_good_bytes
        else:
            path = base_dir / f"sample_{index:05d}.pdf"
            payload = b"not-a-pdf" if is_bad else pdf_good_bytes
        path.write_bytes(payload)
        paths.append(str(path))
    return paths


def _run_once(
    paths: list[str],
    workers: int,
    staged_deep: bool,
    signature_precheck: bool,
) -> float:
    start = time.perf_counter()
    inspect_files(
        paths,
        mode="deep",
        workers=workers,
        use_cache=False,
        staged_deep=staged_deep,
        signature_precheck=signature_precheck,
    )
    return time.perf_counter() - start


def benchmark(
    paths: list[str],
    workers: int,
    repeats: int,
    signature_precheck: bool,
) -> tuple[list[float], list[float]]:
    normal_times: list[float] = []
    staged_times: list[float] = []

    # Warm up import and parser caches.
    _run_once(
        paths[: min(50, len(paths))],
        workers,
        staged_deep=False,
        signature_precheck=signature_precheck,
    )
    _run_once(
        paths[: min(50, len(paths))],
        workers,
        staged_deep=True,
        signature_precheck=signature_precheck,
    )

    for _ in range(repeats):
        normal_times.append(
            _run_once(
                paths,
                workers,
                staged_deep=False,
                signature_precheck=signature_precheck,
            )
        )
        staged_times.append(
            _run_once(
                paths,
                workers,
                staged_deep=True,
                signature_precheck=signature_precheck,
            )
        )
    return normal_times, staged_times


def format_seconds(value: float) -> str:
    return f"{value:.4f}s"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark deep vs staged_deep throughput for mixed good/bad files."
    )
    parser.add_argument("--samples", type=int, default=1200, help="Total file count.")
    parser.add_argument(
        "--bad-ratio",
        type=float,
        default=0.70,
        help="Bad file ratio in [0, 1]. Higher values usually favor staged_deep.",
    )
    parser.add_argument("--workers", type=int, default=8, help="Thread pool workers.")
    parser.add_argument("--repeats", type=int, default=3, help="Benchmark repeats.")
    parser.add_argument(
        "--disable-signature-precheck",
        action="store_true",
        help="Disable signature precheck to compare staged_deep in this mode.",
    )
    args = parser.parse_args()

    if args.samples <= 0:
        raise ValueError("--samples must be > 0")
    if not 0 <= args.bad_ratio <= 1:
        raise ValueError("--bad-ratio must be between 0 and 1")
    if args.workers <= 0:
        raise ValueError("--workers must be > 0")
    if args.repeats <= 0:
        raise ValueError("--repeats must be > 0")

    signature_precheck = not args.disable_signature_precheck

    with tempfile.TemporaryDirectory(prefix="errorfile-bench-") as temp_dir:
        base_dir = Path(temp_dir)
        paths = build_dataset(base_dir, args.samples, args.bad_ratio)
        normal_times, staged_times = benchmark(
            paths,
            args.workers,
            args.repeats,
            signature_precheck=signature_precheck,
        )

    normal_med = statistics.median(normal_times)
    staged_med = statistics.median(staged_times)
    speedup = normal_med / staged_med if staged_med > 0 else float("inf")
    normal_tput = args.samples / normal_med
    staged_tput = args.samples / staged_med

    print("ErrorFile staged_deep benchmark")
    print(f"samples={args.samples} bad_ratio={args.bad_ratio:.2f} workers={args.workers}")
    print(f"signature_precheck={signature_precheck}")
    print(f"deep_only_times={', '.join(format_seconds(t) for t in normal_times)}")
    print(f"staged_deep_times={', '.join(format_seconds(t) for t in staged_times)}")
    print(f"deep_only_median={format_seconds(normal_med)} ({normal_tput:.1f} files/s)")
    print(f"staged_deep_median={format_seconds(staged_med)} ({staged_tput:.1f} files/s)")
    print(f"speedup={speedup:.2f}x")


if __name__ == "__main__":
    main()
