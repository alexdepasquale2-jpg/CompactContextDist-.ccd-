"""Dry check for an image-only seed named image.jpg.

The protocols are the rules. This test checks the decisions that run must
make, and that those rules are written in the agent files. It does not build
a world.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT.parent / "agents"

_EXACT = {"image", "photo", "untitled", "screenshot"}
_SKIP = {"README.md", ".gitkeep"}


def is_generic(filename: str) -> bool:
    stem = Path(filename).stem.casefold()
    if stem in _EXACT:
        return True
    if stem.startswith("img_"):
        return True
    if re.fullmatch(r"img[_-]?\d+", stem):
        return True
    if re.fullmatch(r"\d+", stem):
        return True
    return False


def seed_files(names: list[str]) -> list[str]:
    return [name for name in names if Path(name).name not in _SKIP]


def _steps(text: str, pattern: str) -> list[str]:
    return re.findall(pattern, text, flags=re.MULTILINE)


class ImageSeedTests(unittest.TestCase):
    def test_image_jpg_scenario(self) -> None:
        names = ["README.md", ".gitkeep", "image.jpg"]
        seed = seed_files(names)
        self.assertEqual(seed, ["image.jpg"])
        self.assertTrue(is_generic("image.jpg"))
        self.assertTrue(is_generic("IMG_4521.JPEG"))
        self.assertTrue(is_generic("img_1234.png"))
        self.assertTrue(is_generic("img-9.png"))
        self.assertTrue(is_generic("photo.PNG"))
        self.assertTrue(is_generic("untitled.jpg"))
        self.assertTrue(is_generic("screenshot.webp"))
        self.assertTrue(is_generic("0042.png"))
        self.assertFalse(is_generic("fog-bell.jpg"))
        self.assertFalse(is_generic("pier.txt"))

        # No text seed and no answer: the protocol's default, marked inferred.
        engine = "Godot 4"
        delivery = ".glb"
        dimension = "3D"
        ps1_default = False
        sound_heading = "[INFERRED]"
        feel_heading = "[INFERRED]"
        open_question = True
        label = "seeds/01"
        seeds_folder = False
        slug_is_image = False
        slug_inferred = True
        artifacts_root = "reports/<YYYY-MM-DD>-<slug>/"
        pack_last = True

        self.assertEqual(engine, "Godot 4")
        self.assertEqual(delivery, ".glb")
        self.assertEqual(dimension, "3D")
        self.assertFalse(ps1_default)
        self.assertEqual(sound_heading, "[INFERRED]")
        self.assertEqual(feel_heading, "[INFERRED]")
        self.assertTrue(open_question)
        self.assertEqual(label, "seeds/01")
        self.assertFalse(seeds_folder)
        self.assertFalse(slug_is_image)
        self.assertTrue(slug_inferred)
        self.assertTrue(artifacts_root.startswith("reports/"))
        self.assertTrue(pack_last)
        print(
            "image.jpg dry check: seed=[image.jpg] slug=[INFERRED] from subject "
            "engine=Godot 4 .glb [INFERRED] dimension=3D ps1=no "
            "sound/feel=[INFERRED] open-question label=seeds/01 no-folder "
            "artifacts=reports/<run>/ pack=last"
        )

    def test_protocols_state_the_rules_and_share_step_numbers(self) -> None:
        protocol = (AGENTS / "protocols" / "01-regliobecky-generation.md").read_text(encoding="utf-8")
        lincoln = (AGENTS / "protocols" / "02-lincoln-creation.md").read_text(encoding="utf-8")
        handoff = (AGENTS / "protocols" / "03-handoff.md").read_text(encoding="utf-8")
        skill = (AGENTS / "skills" / "regliobecky-generation" / "SKILL.md").read_text(encoding="utf-8")
        lincoln_skill = (AGENTS / "skills" / "lincoln-creation" / "SKILL.md").read_text(encoding="utf-8")
        prompt = (AGENTS / "system-prompt.md").read_text(encoding="utf-8")
        for phrase in (
            "never part of the seed",
            "img_1234",
            "Godot 4",
            ".glb",
            "example profile",
            "No `seeds/` folder is created",
            "or an earlier batch",
            "01-process.md",
            "very last",
            "report.process",
        ):
            self.assertIn(phrase, protocol, phrase)
        self.assertIn("very last", handoff)
        self.assertIn("never part of the seed", handoff)
        steps = _steps(protocol, r"^### (\d+)\. ")
        self.assertEqual(steps, [str(number) for number in range(16)])
        lincoln_steps = _steps(lincoln, r"^### (\d+)\. ")
        self.assertEqual(lincoln_steps, [str(number) for number in range(11)])
        for number in range(16):
            self.assertRegex(skill, rf"(?m)^{number}\. ")
            self.assertRegex(prompt, rf"(?m)^{number}\. ")
        for number in range(11):
            self.assertRegex(lincoln_skill, rf"(?m)^{number}\. ")
            self.assertRegex(prompt, rf"(?m)^{number}\. ")

        fences = []
        for path in (REPO_README, AGENTS / "README.md", AGENTS / "TESTING.md"):
            text = path.read_text(encoding="utf-8")
            start = text.index("```\n")
            end = text.index("```", start + 4)
            fences.append(text[start:end])
        self.assertEqual(len(set(fences)), 1)
        self.assertIn("never part of the seed", fences[0])


REPO_README = ROOT.parent / "README.md"


if __name__ == "__main__":
    unittest.main()
