import logging

from .middleware import CURRENT_THREAD


class OrganizationIdFilter(logging.Filter):

    def filter(self, record):
        record.organization_id = getattr(CURRENT_THREAD, 'organization_id', None)

        return True


class UserIdFilter(logging.Filter):

    def filter(self, record):
        record.user_id = getattr(CURRENT_THREAD, 'user_id', None)

        return True
