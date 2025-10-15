from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class MyRemoteUserBackend(RemoteUserBackend):
    create_unknown_user = False

    def authenticate(self, request, remote_user):
        # simplified authenticate implementation
        # we are not creating new users
        # only identify users by email
        user = None
        try:
            email = UserModel._default_manager.normalize_email(remote_user)
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            pass
        return user if super().user_can_authenticate(user) else None
