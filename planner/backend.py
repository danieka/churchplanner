from django.core.signing import Signer
from django.contrib.auth.models import User

class HashModelBackend(object):
    def authenticate(self, hash, pk):
        user = User.objects.get(pk=pk)
        signer = Signer()
        value = signer.sign(user.username)
        if value.split(":")[1] == hash:
            return user
        return None
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None