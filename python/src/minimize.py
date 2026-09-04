import argparse
import json
from pathlib import Path

import rcssmin
import rjsmin
from minify_html import minify_html


def __walk(_path: Path) -> list[Path]:
    if _path.is_file():
        return [_path]
    elif _path.is_dir():
        paths = []
        for p in _path.iterdir():
            paths += __walk(p)
        return paths


def main():
    parser = argparse.ArgumentParser(prog='minimize.py')
    parser.add_argument(
        'paths',
        nargs='*',
        default=['../build/'],
    )
    parser.add_argument(
        '--replace',
        action='store_true',
        default=False,
    )
    print(parser.format_help())
    args = parser.parse_args()

    paths = [(Path(__file__).parent / path).resolve(strict=False) for path in args.paths]
    files = []
    for path in paths:
        files += __walk(path)

    for file in files:
        print(file.as_posix())
        suffix = file.suffix
        minified = None
        if suffix in ['.json', '.html', '.js', '.css']:
            content = file.read_text(encoding='utf-8')
            if len(content.splitlines()) <= 1:
                continue

            if suffix in ['.json']:
                minified = json.dumps(json.loads(content), sort_keys=True, separators=(',', ':'))
            elif suffix in ['.html']:
                minified = minify_html.minify(
                    content,
                    minify_js=True,
                    minify_css=True,
                    remove_processing_instructions=True,
                )
            elif suffix in ['.js']:
                minified = rjsmin.jsmin(content, keep_bang_comments=False)
            elif suffix in ['.css']:
                minified = rcssmin.cssmin(content, keep_bang_comments=False)

        if minified is not None:
            if args.replace:
                file.write_text(minified)
            else:
                file.with_suffix('.min' + suffix).write_text(minified)


if __name__ == '__main__':
    main()
