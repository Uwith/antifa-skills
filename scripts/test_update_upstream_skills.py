import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('updater', Path(__file__).with_name('update-upstream-skills.py'))
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class CandidatesTest(unittest.TestCase):
    def test_only_existing_verified_nonarchived_skills_are_updated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            entries = {}
            for name in ['engineering/a', '_local-variants/a', 'utils/template-skill', 'local', 'tracked', 'missing']:
                entries[name] = {'repo_url': 'https://github.com/example/skills.git'}
                if name != 'missing':
                    (root / name).mkdir(parents=True)
                    (root / name / 'SKILL.md').write_text('skill')
            entries['local'] = {}
            entries['tracked']['tracked'] = True
            self.assertEqual(updater.candidates(root, {'entries': entries}), ['engineering/a'])


if __name__ == '__main__':
    unittest.main()
