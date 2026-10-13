from __future__ import annotations


class ApprovalRequired(PermissionError):
    pass


class ApprovalGate:
    """Explicit human-in-the-loop gate for repository mutations."""
    def require(self, approved: bool, action: str):
        if not approved:
            raise ApprovalRequired(f"Human approval is required before: {action}")
        return True
