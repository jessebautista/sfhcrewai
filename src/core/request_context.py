"""
Utility module to help agents track context like requester email.
"""

# Global context for passing information between modules
_request_context = {}

def set_requester_email(email):
    """Set the current requester's email address."""
    global _request_context
    _request_context['email'] = email

def get_requester_email():
    """Get the current requester's email address."""
    global _request_context
    return _request_context.get('email')

def clear_request_context():
    """Clear the request context."""
    global _request_context
    _request_context = {}
