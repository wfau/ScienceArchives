from rest_framework.authentication import RemoteUserAuthentication

class CustomHeaderRemoteUserAuthentication(RemoteUserAuthentication):
    header = "HTTP_X_REMOTE_USER"
