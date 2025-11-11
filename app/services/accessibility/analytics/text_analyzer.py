class TextAnalyzer:
    name = "TextAnalyzer"
    def analyze(self, elements):
        empty_text = sum(1 for e in elements if not e.get("text"))
        return {"analyzer": self.name, "issues_found": empty_text, "score": 100 - empty_text}
