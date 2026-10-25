"""The map/find/focus loop loads less than a full index and less than the markdown."""

from __future__ import annotations

import unittest

from benchmark.attention import measure, table


class AttentionTests(unittest.TestCase):
    def test_focus_loop_beats_full_index_and_whole_markdown(self) -> None:
        try:
            import tiktoken
        except ImportError:
            self.skipTest("tiktoken is not installed")
        stats = measure(tiktoken.get_encoding("o200k_base"))
        print("\n" + table(stats))
        for item in stats:
            self.assertFalse(item.misses, "\n".join(item.misses))
            self.assertGreaterEqual(item.after_hit, item.before_hit)
            self.assertLess(item.after_tokens, item.before_tokens)
            self.assertLess(item.after_waste, item.before_waste)
            self.assertLess(item.after_tokens, item.baseline)


if __name__ == "__main__":
    unittest.main()
