"""Select prebuilt ASCII artwork using Vietnam time; no dependencies or tokens."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VIETNAM = timezone(timedelta(hours=7))
START = '<!-- profile-art:start -->'
END = '<!-- profile-art:end -->'


def period_at(moment):
    if moment.tzinfo is None:
        raise ValueError('Time must include a UTC offset.')
    return 'day' if 6 <= moment.astimezone(VIETNAM).hour < 22 else 'night'


def picture(period):
    if period not in ('day', 'night'):
        raise ValueError('Period must be day or night.')
    return '\n'.join([
        START, '<picture>',
        f'  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/profile/{period}-dark-mobile.svg">',
        f'  <source media="(max-width: 600px)" srcset="assets/profile/{period}-light-mobile.svg">',
        f'  <source media="(prefers-color-scheme: dark)" srcset="assets/profile/{period}-dark.svg">',
        f'  <img src="assets/profile/{period}-light.svg" alt="Nguyen Vu: software engineering, backend and full-stack development. Java, Spring Boot, TypeScript; familiar with Flutter and React Native. Ho Chi Minh City; open to internships." width="1008">',
        '</picture>', END,
    ])


def update_readme(readme, period):
    content = readme.read_text(encoding='utf-8')
    pattern = re.escape(START) + r'.*?' + re.escape(END)
    if len(re.findall(pattern, content, re.S)) != 1:
        raise ValueError('README must contain exactly one profile-art block.')
    updated = re.sub(pattern, lambda _: picture(period), content, flags=re.S)
    if content != updated:
        readme.write_text(updated, encoding='utf-8', newline='\n')
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--period', choices=['auto', 'day', 'night'], default='auto')
    parser.add_argument('--at', help='ISO timestamp with offset, for deterministic previews.')
    args = parser.parse_args()
    moment = datetime.fromisoformat(args.at.replace('Z', '+00:00')) if args.at else datetime.now(VIETNAM)
    period = period_at(moment) if args.period == 'auto' else args.period
    for theme in ('dark', 'light'):
        for suffix in ('', '-mobile'):
            filename = f'{period}-{theme}{suffix}.svg'
            if not (ROOT / 'assets' / 'profile' / filename).is_file():
                raise FileNotFoundError(f'Missing {filename}')
    changed = update_readme(ROOT / 'README.md', period)
    print(f'Profile: {period}; README {"updated" if changed else "unchanged"}.')


if __name__ == '__main__':
    main()
