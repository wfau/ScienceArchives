from django.contrib.auth.middleware import RemoteUserMiddleware

class CustomHeaderRemoteUserMiddleware(RemoteUserMiddleware):
    header = "HTTP_X_REMOTE_USER"
