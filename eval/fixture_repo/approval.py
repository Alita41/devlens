class ApprovalGate:
    def require(self, approved: bool, action: str):
        if not approved:
            raise PermissionError("Human approval required")
        return True
