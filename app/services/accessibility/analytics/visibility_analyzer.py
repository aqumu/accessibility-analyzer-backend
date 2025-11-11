class VisibilityAnalyzer:
    name = "VisibilityAnalyzer"
    def analyze(self, elements):
        hidden = sum(1 for e in elements if e.get("css", {}).get("visibility") == "hidden")
        return {"analyzer": self.name, "issues_found": hidden, "score": 100 - hidden}
