from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, full_name, password=None, **extra_fields):
        """
        Creates and saves a User with the given username, email, full_name and password.
        """
        if not username:
            raise ValueError('The Username must be set')
        if not email:
            raise ValueError('The Email must be set')
        if not full_name:
            raise ValueError('The Full Name must be set')
        
        email = self.normalize_email(email)

        user = self.model(
            username=username,
            email=email,
            full_name=full_name,
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, username, email, full_name, password=None, **extra_fields):
        """
        Creates and saves a superuser (admin) with the given fields.
        """
        # Set default role and staff status
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        
        if extra_fields.get('role') != 'admin':
            raise ValueError('Superuser must have role of admin.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        # Call create_user to do the actual creation
        return self.create_user(username, email, full_name, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    profpict = models.URLField(blank=True, null=True) 
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    
    REQUIRED_FIELDS = ['email', 'full_name']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.role == 'admin'

    def has_module_perms(self, app_label):
        return self.role == 'admin'
