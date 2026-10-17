import os
import tempfile
import unittest
from pathlib import Path

from dodona.dodona_config import DodonaConfig

JUDGE_ROOT = str(Path(__file__).resolve().parents[2])


class TestSanityCheck(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.workdir = tmp.name
        self.addCleanup(os.chdir, Path.cwd())
        os.chdir(self.workdir)

    def config(self, workdir: str, judge: str) -> DodonaConfig:
        return DodonaConfig(
            memory_limit=1,
            time_limit=1,
            programming_language="html",
            natural_language="en",
            resources="",
            source="",
            judge=judge,
            workdir=workdir,
        )

    def test_matching_workdir_and_judge(self):
        self.config(self.workdir, JUDGE_ROOT).sanity_check()

    def test_wrong_workdir(self):
        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        with self.assertRaises(RuntimeError):
            self.config(other.name, JUDGE_ROOT).sanity_check()

    def test_wrong_judge(self):
        wrong = str(Path(self.workdir).resolve())
        with self.assertRaises(RuntimeError) as cm:
            self.config(self.workdir, wrong).sanity_check()
        self.assertIn(JUDGE_ROOT, str(cm.exception))
        self.assertIn(wrong, str(cm.exception))
