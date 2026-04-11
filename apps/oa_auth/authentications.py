from rest_framework_simplejwt.tokens import RefreshToken

def generate_jwt(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)