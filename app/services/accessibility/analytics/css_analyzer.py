class CssAnalyzer:
    name = "CssAnalyzer"
    def analyze(self, elements):
        invis = sum(1 for e in elements if e.get("css", {}).get("display") == "none")
        return {"analyzer": self.name, "issues_found": invis, "score": 100 - invis}
