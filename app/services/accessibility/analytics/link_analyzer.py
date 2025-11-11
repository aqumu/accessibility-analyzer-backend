class LinkAnalyzer:
    name = "LinkAnalyzer"
    def analyze(self, elements):
        bad_links = sum(1 for e in elements if e.get("tag") == "a" and not e.get("attributes", {}).get("href"))
        return {"analyzer": self.name, "issues_found": bad_links, "score": 100 - bad_links}
