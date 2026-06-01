#!/usr/bin/env python3
"""Build source-fragment records for exam-prep workflows."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1('||'.join(parts).encode('utf-8')).hexdigest()[:12]
    return f'{prefix}_{digest}'


def iter_paragraphs(text: str) -> list[str]:
    chunks = [chunk.strip() for chunk in re.split(r'\n\s*\n+', text) if chunk.strip()]
    if chunks:
        return chunks
    return [line.strip() for line in text.splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')


def build(source_paths: list[Path], output_dir: Path) -> None:
    documents: list[dict] = []
    fragments: list[dict] = []
    partitions: list[dict] = []
    support_links: list[dict] = []

    for source_path in source_paths:
        text = source_path.read_text(encoding='utf-8', errors='ignore')
        doc_id = stable_id('source', str(source_path.resolve()), text[:200])
        documents.append({
            'id': doc_id,
            'path': str(source_path),
            'name': source_path.name,
            'sha1': hashlib.sha1(text.encode('utf-8')).hexdigest(),
        })
        for index, paragraph in enumerate(iter_paragraphs(text), start=1):
            fragment_id = stable_id('fragment', doc_id, str(index), paragraph[:120])
            partition_id = stable_id('partition', doc_id, str((index - 1) // 10))
            fragments.append({
                'id': fragment_id,
                'source_id': doc_id,
                'sequence': index,
                'text': paragraph,
            })
            partitions.append({
                'id': partition_id,
                'source_id': doc_id,
                'fragment_id': fragment_id,
            })
            support_links.append({
                'from': fragment_id,
                'to': doc_id,
                'type': 'supported_by_source',
            })

    write_jsonl(output_dir / 'source_documents.jsonl', documents)
    write_jsonl(output_dir / 'source_fragments.jsonl', fragments)
    write_jsonl(output_dir / 'fragment_partitions.jsonl', partitions)
    write_jsonl(output_dir / 'support_links.jsonl', support_links)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('sources', nargs='+', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    build(args.sources, args.output_dir)


if __name__ == '__main__':
    main()
