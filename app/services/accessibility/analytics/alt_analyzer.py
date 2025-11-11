class AltAnalyzer:
    name = "AltAnalyzer"
    def analyze(self, elements):
        missing = sum(1 for e in elements if not e.get("attributes", {}).get("alt"))
        return {"analyzer": self.name, "issues_found": missing, "score": 100 - missing}
