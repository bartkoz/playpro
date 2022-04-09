from django.dispatch import Signal

invitation_revoked = Signal()
invitation_created = Signal()
invitation_denied = Signal()
