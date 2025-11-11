class RoleAnalyzer:
    name = "RoleAnalyzer"
    def analyze(self, elements):
        no_role = sum(1 for e in elements if not e.get("role"))
        return {"analyzer": self.name, "issues_found": no_role, "score": 100 - no_role}
