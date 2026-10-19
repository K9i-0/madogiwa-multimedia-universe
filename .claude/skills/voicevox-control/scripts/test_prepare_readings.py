#!/usr/bin/env python3
"""Regression checks for subtitle preservation and context-sensitive readings."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from prepare_readings import DEFAULT_DICTIONARY, load_dictionary, prepare_row


class ReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dictionary = load_dictionary()

    def prepare(self, text, scopes=(), **fields):
        return prepare_row({"id": "test", "text": text, **fields}, self.dictionary, scopes)

    def load_local(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "local.json"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return load_dictionary(local_path=path)

    def test_preserves_subtitles_and_metadata(self):
        row = {"id": "scene-1", "text": "管理人が祠を見た。", "speaker": "narrator"}
        result = prepare_row(row, self.dictionary)
        self.assertEqual(result["text"], row["text"])
        self.assertEqual(result["id"], row["id"])
        self.assertEqual(result["speaker"], row["speaker"])
        self.assertNotIn("speech", row)
        self.assertEqual(result["speech"], "カンリニンがホコラを見た。")
        self.assertEqual(result["reading_report"]["review"], [])

    def test_empty_and_sky_are_not_conflated(self):
        text = "空の缶、空の色、空の部屋、空き缶、空席、空気。"
        result = self.prepare(text)
        self.assertEqual(result["speech"], "カラの缶、空の色、カラの部屋、アキカン、クウセキ、空気。")
        positions = [r["start"] for r in result["reading_report"]["review"]]
        self.assertEqual(positions, [text.index("空の色"), text.index("空気")])

    def test_person_direction_counter_and_sky_need_context(self):
        for text in ("明日来る方がいい。", "こちらに来る方です。", "夕方の方法。",
                     "あの人と三人の日本人。", "今年の分は三十分。",
                     "一杯、三杯、乾杯。", "日の行い。", "その間、間を置く。",
                     "学校に通っている。", "道を通って帰る。", "弓の弦。"):
            with self.subTest(text=text):
                result = self.prepare(text)
                self.assertEqual(result["speech"], text)
                self.assertTrue(result["reading_report"]["review"])

    def test_project_intro_readings(self):
        self.assertEqual(self.prepare("大まじめな映像。大きな会社。") ["speech"], "オオマジメな映像。大きな会社。")
        self.assertEqual(self.prepare("立ち飲み処は各話に登場。", scopes=["mmu"])["speech"], "タチノミドコロはカクワに登場。")
        self.assertEqual(self.prepare("各話数の比較。") ["speech"], "各話数の比較。")
        self.assertEqual(self.prepare("立ち飲み処。") ["speech"], "立ち飲み処。")

    def test_compound_kanji_are_not_partially_replaced(self):
        result = self.prepare("祠と祠堂。中口さんと田中口調。", scopes=["mmu"])
        self.assertEqual(result["speech"], "ホコラと祠堂。ナカグチさんと田中口調。")

    def test_scopes_and_ascii_boundaries(self):
        text = "福ギュンとY村でIT企業、GitHub、Git、GITHUB、FACTOR、MYAPI、my_Git。"
        self.assertEqual(self.prepare(text)["speech"], text)
        result = self.prepare(text, scopes=["mmu", "tech", "y-village"])
        self.assertEqual(result["speech"],
                         "フクギュンとワイむらでアイティー企業、ギットハブ、ギット、GITHUB、FACTOR、MYAPI、my_Git。")
        with self.assertRaisesRegex(ValueError, "Unknown scope"):
            self.prepare(text, scopes=["typo"])

    def test_longest_match_and_repeated_occurrences(self):
        result = self.prepare("Flutter SceneとFlutter。GitHubとGitHub。", scopes=["tech"])
        self.assertEqual(result["speech"], "フラッターシーンとフラッター。ギットハブとギットハブ。")
        self.assertEqual(len(result["reading_report"]["applied"]), 4)

    def test_manual_reading_is_verbatim(self):
        result = self.prepare("管理人がこちらに来る方です。",
                              speech_override="管理人がこちらに来るカタです。")
        self.assertEqual(result["speech"], "管理人がこちらに来るカタです。")
        self.assertEqual(result["reading_report"]["method"], "explicit")
        self.assertEqual(result["reading_report"]["applied"], [])
        self.assertEqual(result["reading_report"]["review"], [])
        with self.assertRaisesRegex(ValueError, "speech_override"):
            self.prepare("本文", speech_override="")

    def test_local_override_and_no_cascading(self):
        local = {"schema_version": 1, "replacements": [
            {"id": "common.kanrinin", "surface": "管理人", "reading": "かんりにん",
             "source": "test", "note": "same-id override"},
            {"id": "test.empty", "surface": "空の缶", "reading": "空き缶",
             "source": "test", "note": "overlapping local rule; not a new shared entry"},
        ]}
        dictionary = self.load_local(local)
        result = prepare_row({"text": "管理人と空の缶。"}, dictionary)
        self.assertEqual(result["speech"], "かんりにんと空き缶。")
        self.assertNotEqual(dictionary["sha256"], self.dictionary["sha256"])

    def test_invalid_dictionary_rejected(self):
        entry = {"id": "test.x", "surface": "語", "reading": "ゴ", "source": "test", "note": "test"}
        cases = [
            {"schema_version": 2},
            {"schema_version": 1, "replacements": [entry, entry]},
            {"schema_version": 1, "replacements": [{**entry, "reading": ""}]},
            {"schema_version": 1, "replacements": [{**entry, "scope": "missing"}]},
            {"schema_version": 1, "replacements": [{**entry, "match": "regexp"}]},
        ]
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.load_local(data)

    def test_cli_from_another_directory_and_no_input_overwrite(self):
        script = Path(__file__).resolve().with_name("prepare_readings.py")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            target = Path(directory) / "prepared.json"
            original = '[{"id":"x","text":"祠の前に空の缶がある。"}]'
            source.write_text(original, encoding="utf-8")
            command = [sys.executable, str(script), "--input", str(source)]
            completed = subprocess.run(command + ["--output", str(target)], cwd=directory,
                                       capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))[0]["speech"],
                             "ホコラの前にカラの缶がある。")
            rejected = subprocess.run(command + ["--output", str(source)], cwd=directory,
                                      capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 2)
            self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_dictionary_sources_are_documented(self):
        raw = json.loads(DEFAULT_DICTIONARY.read_text(encoding="utf-8"))
        for group in ("replacements", "context_checks"):
            for rule in raw[group]:
                with self.subTest(rule=rule["id"]):
                    self.assertIn(rule["source"], raw["sources"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
