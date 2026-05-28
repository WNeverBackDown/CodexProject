import re


URL_RE = re.compile(r"https?://[^\s，。；、]+", re.IGNORECASE)


def normalize_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def extract_url(text):
    match = URL_RE.search(text or "")
    return match.group(0) if match else ""


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError("配置必须是 JSON 对象")

    settings = config.setdefault("settings", {})
    if not isinstance(settings, dict):
        raise ValueError("settings 必须是对象")

    settings["dedupe_minutes"] = int(settings.get("dedupe_minutes", 30))
    settings["max_alerts"] = int(settings.get("max_alerts", 200))

    rules = config.setdefault("rules", [])
    if not isinstance(rules, list):
        raise ValueError("rules 必须是数组")

    seen_ids = set()
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValueError("第 %s 条规则必须是对象" % (index + 1))
        rule["id"] = str(rule.get("id") or "rule-%s" % (index + 1))
        if rule["id"] in seen_ids:
            raise ValueError("规则 id 重复: %s" % rule["id"])
        seen_ids.add(rule["id"])
        rule["name"] = str(rule.get("name") or rule["id"])
        rule["enabled"] = bool(rule.get("enabled", True))
        rule["terms"] = _clean_list(rule.get("terms"))
        rule["exclude"] = _clean_list(rule.get("exclude"))
        if not rule["terms"]:
            raise ValueError("规则 %s 至少需要一个关键词" % rule["name"])
    return config


def _clean_list(value):
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    cleaned = []
    for item in value:
        text = str(item or "").strip()
        if text:
            cleaned.append(text)
    return cleaned


class RuleEngine:
    def __init__(self, config):
        self.config = validate_config(config)

    def match(self, message):
        text = normalize_text("%s %s %s" % (message.room, message.sender, message.content))
        matches = []
        for rule in self.config.get("rules", []):
            if not rule.get("enabled", True):
                continue
            if _contains_any(text, rule.get("exclude", [])):
                continue
            matched_terms = [term for term in rule.get("terms", []) if normalize_text(term) in text]
            if matched_terms:
                matches.append(
                    {
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "matched_terms": matched_terms,
                    }
                )
        return matches


def _contains_any(text, terms):
    for term in terms:
        if normalize_text(term) in text:
            return True
    return False
