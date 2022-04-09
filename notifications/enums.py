from enum import Enum


class NotificationTypes(Enum):

    INVITATION = "invitation"
    INVITATION_REVOKE = "invitation_revoke"
    INVITATION_REFUSED = "invitation_refused"
