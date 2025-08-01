"""
CPT Version Management System
This module provides version control and change tracking for CPT definitions.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class ChangeType(Enum):
    """Types of changes to CPTs."""
    ADDED = "added"
    UPDATED = "updated"
    VALIDATED = "validated"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class VersionRecord:
    """Record of a version change."""
    cpt_id: str
    version: str
    change_type: ChangeType
    timestamp: datetime
    changed_by: str = "system"
    change_notes: str = ""
    previous_version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cpt_id": self.cpt_id,
            "version": self.version,
            "change_type": self.change_type.value,
            "timestamp": self.timestamp.isoformat(),
            "changed_by": self.changed_by,
            "change_notes": self.change_notes,
            "previous_version": self.previous_version
        }


class CPTVersionManager:
    """
    Version management system for CPT library.
    Tracks all changes to CPT definitions with full audit trail.
    """

    def __init__(self):
        """Initialize version manager."""
        self.version_history: Dict[str, List[VersionRecord]] = {}
        self.current_versions: Dict[str, str] = {}

    def track_version(self, cpt_id: str, version: str, change_type: str,
                      changed_by: str = "system", notes: str = "") -> None:
        """
        Track a version change.
        Args:
            cpt_id: CPT identifier
            version: New version
            change_type: Type of change
            changed_by: Who made the change
            notes: Change notes
        """
        if cpt_id not in self.version_history:
            self.version_history[cpt_id] = []
        previous_version = self.current_versions.get(cpt_id)
        record = VersionRecord(
            cpt_id=cpt_id,
            version=version,
            change_type=ChangeType(change_type),
            timestamp=datetime.now(),
            changed_by=changed_by,
            change_notes=notes,
            previous_version=previous_version
        )
        self.version_history[cpt_id].append(record)
        self.current_versions[cpt_id] = version

    def get_version_history(self, cpt_id: str) -> List[VersionRecord]:
        """Get version history for a CPT."""
        return self.version_history.get(cpt_id, [])

    def get_current_version(self, cpt_id: str) -> Optional[str]:
        """Get current version of a CPT."""
        return self.current_versions.get(cpt_id)

    def get_latest_changes(self, limit: int = 10) -> List[VersionRecord]:
        """Get latest changes across all CPTs."""
        all_records = []
        for records in self.version_history.values():
            all_records.extend(records)
        # Sort by timestamp descending
        all_records.sort(key=lambda r: r.timestamp, reverse=True)
        return all_records[:limit]

    def export_history(self) -> Dict[str, Any]:
        """Export version history."""
        return {
            "version_history": {
                cpt_id: [record.to_dict() for record in records]
                for cpt_id, records in self.version_history.items()
            },
            "current_versions": self.current_versions.copy(),
            "export_timestamp": datetime.now().isoformat()
        }
