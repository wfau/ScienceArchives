from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth import get_user_model

import logging
logger = logging.getLogger(__name__)

UserModel = get_user_model()

class MyRemoteUserBackend(RemoteUserBackend):
    create_unknown_user = False

    def authenticate(self, request, remote_user):
        # simplified authenticate implementation
        # we are not creating new users
        # only identify users by email
        user = None
        email = UserModel._default_manager.normalize_email(remote_user)
        user, created = UserModel._default_manager.get_or_create(email=email, defaults={'username': email[:150]})
        if created:
            logger.info(f'New user: "{email}"')
        return user if super().user_can_authenticate(user) else None
