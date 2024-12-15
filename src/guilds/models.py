from django.db import models


class Guild(models.Model):
    id = models.AutoField(primary_key=True)
    gid = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    members = models.ManyToManyField('accounts.Account', related_name='guilds')

    def __str__(self):
        return self.name
