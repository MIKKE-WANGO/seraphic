from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from cloudinary.models import CloudinaryField

# Create your models here.

#custom user manager
class UserAccountManager(BaseUserManager):

    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have email address')

        #ensure emails are consistent
        email = self.normalize_email(email)
        email = email.lower()

        #create user
        user = self.model(
            email = email,
            name = name,
            
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user    

class UserAccount(AbstractBaseUser, PermissionsMixin):

    #i can add any other fields i would want a user to have such as phone number
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserAccountManager()

    #determine what default login will be 
    #Normally it is 'username' but i want to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name' ]

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name
    
    def __str__(self):
        return self.email


class ResetPasswordCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    date_created = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True)