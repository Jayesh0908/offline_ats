"""
Command-line interface for Offline ATS.

This gives the project a non-Streamlit build path for terminal demos and
offline submission workflows.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

import config
from database.db import (
    delete_all_candidates,
    delete_candidate,
    get_all_candidates,
    get_candidate_by_id,
    get_candidate_count,
    init_db,
    insert_candidate,
    search_candidates_fts,
)
from embeddings.embedder import create_resume_embedding
from extraction.text_extractor import extract_text
from llm.local_llm import parse_resume
from matching.matcher import rank_candidates, search_candidates


def _json_load(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _row_to_dict(row: Any) -> Dict[str, Any]:
    data = dict(row)
    data["skills"] = _json_load(data.get("skills"), [])
    data["education"] = _json_load(data.get("education"), [])
    data["experience"] = _json_load(data.get("experience"), [])
    data["projects"] = _json_load(data.get("projects"), [])
    data["json_data"] = _json_load(data.get("json_data"), {})
    data.pop("embedding", None)
    return data


def _print_table(headers: List[str], rows: Iterable[List[Any]]) -> None:
    rows = [[str(cell) for cell in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]

    def fmt(row: List[Any]) -> str:
        return "  ".join(str(cell).ljust(width) for cell, width in zip(row, widths))

    print(fmt(headers))
    print(fmt(["-" * width for width in widths]))
    for row in rows:
        print(fmt(row))


def _read_text_arg(text: str | None, file_path: str | None, label: str) -> str:
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    if text:
        return text
    raise SystemExit(f"Provide {label} text or --{label}-file.")


def _candidate_summary(row: Any) -> List[Any]:
    candidate = dict(row)
    skills = _json_load(candidate.get("skills"), [])
    return [
        candidate.get("id", ""),
        candidate.get("name", "") or "Unknown",
        candidate.get("email", ""),
        ", ".join(skills[:5]),
    ]


def command_init(_: argparse.Namespace) -> int:
    init_db()
    print(f"Database ready: {config.DATABASE_PATH}")
    return 0


def command_process(args: argparse.Namespace) -> int:
    init_db()
    processed = 0
    failed = 0

    for raw_path in args.files:
        source_path = Path(raw_path).expanduser().resolve()
        if not source_path.exists():
            print(f"ERROR: file not found: {source_path}", file=sys.stderr)
            failed += 1
            continue

        file_path = source_path
        if args.copy_to_uploads:
            config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            file_path = config.UPLOAD_DIR / source_path.name
            counter = 1
            while file_path.exists():
                file_path = config.UPLOAD_DIR / f"{source_path.stem}_{counter}{source_path.suffix}"
                counter += 1
            shutil.copy2(source_path, file_path)

        print(f"Processing: {file_path}")
        resume_text = extract_text(str(file_path))
        if not resume_text.strip():
            print(f"ERROR: no text extracted from {file_path}", file=sys.stderr)
            failed += 1
            continue

        parsed = parse_resume(resume_text)
        skills = parsed.get("skills", []) if isinstance(parsed, dict) else []
        embedding = None if args.no_embedding else create_resume_embedding(resume_text, skills)

        candidate_id = insert_candidate(
            name=parsed.get("name", ""),
            email=parsed.get("email", ""),
            phone=parsed.get("phone", ""),
            skills=skills,
            education=parsed.get("education", []),
            experience=parsed.get("experience", []),
            projects=parsed.get("projects", []),
            resume_path=str(file_path),
            resume_text=resume_text,
            json_data=parsed,
            embedding=embedding,
        )
        print(f"Saved candidate #{candidate_id}: {parsed.get('name') or 'Unknown'}")
        processed += 1

    print(f"Done. processed={processed} failed={failed}")
    return 1 if failed and not processed else 0


def command_list(args: argparse.Namespace) -> int:
    init_db()
    candidates = get_all_candidates()
    if args.limit:
        candidates = candidates[: args.limit]
    if not candidates:
        print("No candidates found.")
        return 0
    _print_table(["ID", "Name", "Email", "Top Skills"], [_candidate_summary(row) for row in candidates])
    print(f"\nTotal candidates: {get_candidate_count()}")
    return 0


def command_show(args: argparse.Namespace) -> int:
    init_db()
    row = get_candidate_by_id(args.candidate_id)
    if not row:
        print(f"Candidate not found: {args.candidate_id}", file=sys.stderr)
        return 1
    print(json.dumps(_row_to_dict(row), indent=2, default=str))
    return 0


def command_rank(args: argparse.Namespace) -> int:
    init_db()
    jd_text = _read_text_arg(args.jd, args.jd_file, "jd")
    results = rank_candidates(jd_text)
    if args.limit:
        results = results[: args.limit]
    if not results:
        print("No candidates to rank.")
        return 0

    rows = [
        [
            result.candidate_id,
            result.name or "Unknown",
            f"{result.final_score:.1%}",
            f"{result.embedding_score:.1%}",
            f"{result.skill_score:.1%}",
        ]
        for result in results
    ]
    _print_table(["ID", "Name", "Final", "Embedding", "Skills"], rows)
    return 0


def command_search(args: argparse.Namespace) -> int:
    init_db()
    if args.keyword:
        results = [dict(row) for row in search_candidates_fts(args.query)]
        for row in results:
            row["search_score"] = 0.5
    else:
        results = search_candidates(args.query)
    if args.limit:
        results = results[: args.limit]
    if not results:
        print("No matching candidates found.")
        return 0

    rows = [
        [
            row.get("id", ""),
            row.get("name", "") or "Unknown",
            row.get("email", ""),
            row.get("search_score", ""),
        ]
        for row in results
    ]
    _print_table(["ID", "Name", "Email", "Score"], rows)
    return 0


def command_export(args: argparse.Namespace) -> int:
    init_db()
    data = [_row_to_dict(row) for row in get_all_candidates()]
    output = json.dumps(data, indent=2, default=str)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Exported {len(data)} candidates to {args.output}")
    else:
        print(output)
    return 0


def command_delete(args: argparse.Namespace) -> int:
    init_db()
    delete_candidate(args.candidate_id)
    return 0


def command_clear(args: argparse.Namespace) -> int:
    init_db()
    if not args.yes:
        print("Refusing to clear database without --yes.", file=sys.stderr)
        return 1
    delete_all_candidates()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="offline-ats",
        description="Offline ATS command-line interface",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_cmd = subparsers.add_parser("init", help="Initialize the SQLite database")
    init_cmd.set_defaults(func=command_init)

    process_cmd = subparsers.add_parser("process", help="Process resume files into the database")
    process_cmd.add_argument("files", nargs="+", help="PDF, PNG, JPG, or JPEG resume files")
    process_cmd.add_argument("--copy-to-uploads", action="store_true", help="Copy files into uploaded_resumes/")
    process_cmd.add_argument("--no-embedding", action="store_true", help="Skip embedding generation")
    process_cmd.set_defaults(func=command_process)

    list_cmd = subparsers.add_parser("list", help="List stored candidates")
    list_cmd.add_argument("--limit", type=int, default=0, help="Maximum rows to show")
    list_cmd.set_defaults(func=command_list)

    show_cmd = subparsers.add_parser("show", help="Show a candidate as JSON")
    show_cmd.add_argument("candidate_id", type=int)
    show_cmd.set_defaults(func=command_show)

    rank_cmd = subparsers.add_parser("rank", help="Rank candidates against a job description")
    rank_cmd.add_argument("--jd", help="Job description text")
    rank_cmd.add_argument("--jd-file", help="Path to a job description text file")
    rank_cmd.add_argument("--limit", type=int, default=0, help="Maximum rows to show")
    rank_cmd.set_defaults(func=command_rank)

    search_cmd = subparsers.add_parser("search", help="Search candidates")
    search_cmd.add_argument("query", help="Search query")
    search_cmd.add_argument("--keyword", action="store_true", help="Use SQLite keyword search only")
    search_cmd.add_argument("--limit", type=int, default=0, help="Maximum rows to show")
    search_cmd.set_defaults(func=command_search)

    export_cmd = subparsers.add_parser("export", help="Export candidates as JSON")
    export_cmd.add_argument("--output", "-o", help="Write JSON to a file instead of stdout")
    export_cmd.set_defaults(func=command_export)

    delete_cmd = subparsers.add_parser("delete", help="Delete one candidate")
    delete_cmd.add_argument("candidate_id", type=int)
    delete_cmd.set_defaults(func=command_delete)

    clear_cmd = subparsers.add_parser("clear", help="Delete all candidates")
    clear_cmd.add_argument("--yes", action="store_true", help="Confirm clearing the database")
    clear_cmd.set_defaults(func=command_clear)

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
