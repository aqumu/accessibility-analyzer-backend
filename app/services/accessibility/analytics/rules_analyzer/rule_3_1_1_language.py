from app.services.accessibility.analytics.json_parser.models import DocumentInfo

class Rule311Language:
    id = "3.1.1"
    description = "Pages need language specification"

    def check(self, document: DocumentInfo) -> bool:
        if(document.lang == None):
            return False
        return True
