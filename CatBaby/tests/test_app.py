import os
import shutil
import tempfile
import unittest

from catbaby.app import CatBabyApp
from catbaby.storage import write_json


class CatBabyAppTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="catbaby-test-")
        os.makedirs(os.path.join(self.root, "config"), exist_ok=True)
        write_json(
            os.path.join(self.root, "config", "default_rules.json"),
            {
                "settings": {"dedupe_minutes": 30, "max_alerts": 200},
                "rules": [
                    {
                        "id": "food",
                        "name": "猫粮",
                        "enabled": True,
                        "terms": ["猫粮"],
                        "exclude": ["已结束"],
                    }
                ],
            },
        )

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_process_message_creates_alert_once_in_dedupe_window(self):
        app = CatBabyApp(self.root)
        first = app.process_payload({"content": "猫粮限时好价 https://example.com"})
        second = app.process_payload({"content": "猫粮限时好价 https://example.com"})
        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])

    def test_update_config_validation(self):
        app = CatBabyApp(self.root)
        with self.assertRaises(ValueError):
            app.update_config({"settings": {}, "rules": [{"id": "bad", "terms": []}]})


if __name__ == "__main__":
    unittest.main()
