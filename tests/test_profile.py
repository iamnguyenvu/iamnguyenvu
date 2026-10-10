import importlib.util
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

spec = importlib.util.spec_from_file_location('profile', Path(__file__).resolve().parents[1] / 'scripts/update_profile.py')
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)


class ProfileTests(unittest.TestCase):
    def test_vietnam_boundaries(self):
        for timestamp, expected in [
            ('2026-10-10T05:59:59+07:00', 'night'),
            ('2026-10-10T06:00:00+07:00', 'day'),
            ('2026-10-10T21:59:59+07:00', 'day'),
            ('2026-10-10T22:00:00+07:00', 'night'),
            ('2026-10-09T23:00:00+00:00', 'day'),
            ('2026-10-10T15:00:00+00:00', 'night'),
        ]:
            with self.subTest(timestamp=timestamp):
                self.assertEqual(profile.period_at(datetime.fromisoformat(timestamp)), expected)

    def test_preserves_biography_and_is_idempotent(self):
        with TemporaryDirectory() as folder:
            readme = Path(folder) / 'README.md'
            readme.write_text('Intro\n' + profile.picture('day') + '\nBio\n', encoding='utf-8')
            self.assertTrue(profile.update_readme(readme, 'night'))
            self.assertEqual(readme.read_text(encoding='utf-8'), 'Intro\n' + profile.picture('night') + '\nBio\n')
            self.assertFalse(profile.update_readme(readme, 'night'))

    def test_rejects_missing_block_and_naive_time(self):
        with TemporaryDirectory() as folder:
            readme = Path(folder) / 'README.md'
            readme.write_text('Biography only', encoding='utf-8')
            with self.assertRaises(ValueError):
                profile.update_readme(readme, 'day')
        with self.assertRaises(ValueError):
            profile.period_at(datetime(2026, 10, 10, 6))
