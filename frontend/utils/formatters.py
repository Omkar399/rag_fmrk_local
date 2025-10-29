"""Formatting utilities for the Streamlit UI."""


def format_file_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_session_id(session_id: str, length: int = 12) -> str:
    """Format session ID for display."""
    return session_id[:length] + "..."


def format_message(msg: dict) -> str:
    """Format message for display."""
    return msg.get("content", "")
