class JWTRevokedError(Exception):
    def __init__(self, message="JWT token was revoked."):
        self.message = message

    def __str__(self):
        return self.message


class EnvVariableError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
