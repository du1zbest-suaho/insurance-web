"""
run_tests.py — 테스트 실행 및 결과 기록

사용법:
    python tests/run_tests.py              # 전체 테스트
    python tests/run_tests.py test_api     # 특정 파일
    python tests/run_tests.py -k keyword  # 키워드 필터

결과: tests/TEST_RESULTS.md 에 자동 기록
"""

import subprocess
import sys
import os
from datetime import datetime

# Windows 터미널 CP949 인코딩 문제 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "cp1252", "mbcs"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "TEST_RESULTS.md")
TESTS_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(TESTS_DIR)


def run_pytest(extra_args: list[str]) -> tuple[str, int]:
    """pytest 실행 후 (출력, 종료코드) 반환"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--no-header",
        "-p", "no:warnings",
    ] + extra_args

    result = subprocess.run(
        cmd,
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout + result.stderr, result.returncode


def parse_summary(output: str) -> dict:
    """pytest 출력에서 요약 정보 추출"""
    summary = {
        "passed": 0,
        "failed": 0,
        "error": 0,
        "skipped": 0,
        "total": 0,
        "duration": "",
        "result": "UNKNOWN",
    }
    for line in output.splitlines():
        # 예: "121 passed, 837 warnings in 48.65s"
        if "passed" in line or "failed" in line or "error" in line:
            if line.strip().startswith("="):
                parts = line.strip("= \n").split(",")
                for part in parts:
                    part = part.strip()
                    if "passed" in part:
                        summary["passed"] = int(part.split()[0])
                    elif "failed" in part:
                        summary["failed"] = int(part.split()[0])
                    elif "error" in part:
                        summary["error"] = int(part.split()[0])
                    elif "skipped" in part:
                        summary["skipped"] = int(part.split()[0])
                    if "in " in part and "s" in part:
                        summary["duration"] = part.split("in ")[-1].strip()
                break

    summary["total"] = summary["passed"] + summary["failed"] + summary["error"]
    if summary["failed"] == 0 and summary["error"] == 0 and summary["total"] > 0:
        summary["result"] = "PASS"
    elif summary["total"] > 0:
        summary["result"] = "FAIL"
    return summary


def extract_failures(output: str) -> list[str]:
    """실패한 테스트 목록 추출"""
    failures = []
    for line in output.splitlines():
        if "FAILED" in line and "::" in line:
            # "tests/test_api.py::TestFoo::test_bar FAILED" 형식
            test_id = line.strip().replace("FAILED", "").strip()
            failures.append(test_id)
    return failures


def extract_passed(output: str) -> list[str]:
    """통과한 테스트 목록 추출"""
    passed = []
    for line in output.splitlines():
        if "PASSED" in line and "::" in line:
            test_id = line.strip().replace("PASSED", "").strip()
            # 진행률 제거 예: "[ 3%]"
            if "[" in test_id:
                test_id = test_id[:test_id.rfind("[")].strip()
            passed.append(test_id)
    return passed


def write_results(output: str, summary: dict, extra_args: list[str]) -> None:
    """TEST_RESULTS.md 에 결과 추가"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icon = "✅" if summary["result"] == "PASS" else "❌"
    filter_info = " ".join(extra_args) if extra_args else "전체"

    failures = extract_failures(output)
    passed_list = extract_passed(output)

    lines = [
        f"\n---\n",
        f"## {icon} {now} — {summary['result']} ({filter_info})\n",
        f"\n",
        f"| 항목 | 결과 |\n",
        f"|---|---|\n",
        f"| 전체 | {summary['total']} |\n",
        f"| 통과 | {summary['passed']} |\n",
        f"| 실패 | {summary['failed']} |\n",
        f"| 오류 | {summary['error']} |\n",
        f"| 건너뜀 | {summary['skipped']} |\n",
        f"| 소요시간 | {summary['duration']} |\n",
        f"\n",
    ]

    if failures:
        lines.append("### 실패한 테스트\n")
        for f in failures:
            lines.append(f"- ❌ `{f}`\n")
        lines.append("\n")

        # 실패 상세 출력 추출
        lines.append("<details><summary>실패 상세 로그</summary>\n\n```\n")
        in_failure = False
        for line in output.splitlines():
            if line.startswith("FAILED") or "_ FAILED _" in line or "_ ERROR _" in line:
                in_failure = True
            if in_failure:
                lines.append(line + "\n")
            if in_failure and line.startswith("====="):
                break
        lines.append("```\n\n</details>\n\n")

    else:
        lines.append(f"### 통과한 테스트 ({len(passed_list)}개)\n")
        # 파일별 그룹화
        by_file: dict[str, list[str]] = {}
        for t in passed_list:
            fname = t.split("::")[0] if "::" in t else t
            fname = fname.replace("tests/", "").replace("tests\\", "")
            by_file.setdefault(fname, []).append(t)
        for fname, tests in sorted(by_file.items()):
            lines.append(f"\n**{fname}** ({len(tests)}개)\n")
            for t in tests:
                short = t.split("::")[-1] if "::" in t else t
                lines.append(f"- ✅ `{short}`\n")
        lines.append("\n")

    # 파일에 추가
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.writelines(lines)


def ensure_header() -> None:
    """TEST_RESULTS.md 헤더 초기화 (파일 없을 때만)"""
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            f.write("# 테스트 결과 기록\n\n")
            f.write("> `python tests/run_tests.py` 실행 시 자동 기록됩니다.\n")
            f.write("> 시나리오 명세: [TEST_SCENARIOS.md](TEST_SCENARIOS.md)\n")


def main() -> None:
    extra_args = sys.argv[1:]

    ensure_header()

    print("=" * 60)
    print(f"테스트 실행중... ({' '.join(extra_args) if extra_args else '전체'})")
    print("=" * 60)

    output, returncode = run_pytest(extra_args)
    print(output)

    summary = parse_summary(output)
    write_results(output, summary, extra_args)

    icon = "✅ PASS" if summary["result"] == "PASS" else "❌ FAIL"
    print("=" * 60)
    print(f"결과: {icon}  |  통과: {summary['passed']}  |  실패: {summary['failed']}  |  {summary['duration']}")
    print(f"기록: {RESULTS_FILE}")
    print("=" * 60)

    sys.exit(returncode)


if __name__ == "__main__":
    main()
