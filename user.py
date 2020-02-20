import bcrypt
from datetime import datetime as dt
import secrets

from models import MongoModel, RedisModel

class User(MongoModel):
    def __init__(self, password):
        self.salt = bcrypt.gensalt()
        self.hash_password = bcrypt.hashpw(password.encode(), self.salt)
        self.access_token_id = None 
        self._access_token = None
        self.refresh_token_id = None
        self._refresh_token = None

    @property
    def authorized_users(self):
        return [self.pk]

    @property
    def access_token(self):
        pass

    @property 
    def refresh_token(self):
        pass

    def is_authorized(self, resource):
        return self.pk in resource.authorized_users

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.hash_password)

    def generate_access_token(self, refresh_token):
        if self.refresh_token == refresh_token:
            access_token = AccessToken()
            access_token.save()
            self.access_token_id = access_token.pk



class Token(RedisModel):
    lifetime = None 

    def __init__(self, lifetime=None):
        self.token = secrets.token_urlsafe()
        self.lifetime = lifetime or self.__class__.lifetime
        self.expire_date = dt.now() + self.lifetime

    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return self.token == other.token 

    def is_expired(self):
        return dt.now() > self.expire_date 


class AccessToken(Token):
    lifetime = timedelta(days=1)


class RefreshToken(Token):
    lifetime = timedelta(days=8)