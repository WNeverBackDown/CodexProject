import unittest

from catbaby.models import Message
from catbaby.rules import RuleEngine, extract_url


class RuleEngineTest(unittest.TestCase):
    def test_matches_enabled_rule(self):
        engine = RuleEngine(
            {
                "settings": {"dedupe_minutes": 30},
                "rules": [
                    {
                        "id": "food",
                        "name": "猫粮",
                        "enabled": True,
                        "terms": ["猫粮", "主食罐"],
                        "exclude": ["已结束"],
                    }
                ],
            }
        )
        message = Message.from_dict({"room": "猫群", "sender": "A", "content": "主食罐限时好价"})
        matches = engine.match(message)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["matched_terms"], ["主食罐"])

    def test_exclude_blocks_match(self):
        engine = RuleEngine(
            {
                "settings": {},
                "rules": [
                    {
                        "id": "food",
                        "name": "猫粮",
                        "enabled": True,
                        "terms": ["猫粮"],
                        "exclude": ["已结束"],
                    }
                ],
            }
        )
        message = Message.from_dict({"content": "猫粮优惠已结束"})
        self.assertEqual(engine.match(message), [])

    def test_extract_url(self):
        self.assertEqual(extract_url("看这个 https://example.com/a?b=1，快"), "https://example.com/a?b=1")


if __name__ == "__main__":
    unittest.main()
