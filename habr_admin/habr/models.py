from datetime import datetime
from django.db import models


class Hub(models.Model):
    name = models.CharField(max_length=200,
                            )
    url = models.URLField()
    period = models.IntegerField(verbose_name='Period, min',
                                 default=10,
                                 )
    nextcall = models.DateTimeField(default=datetime.now,
                                    )

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100,
                            unique=True,
                            )
    url = models.URLField()

    def __str__(self):
        return self.name


class Post(models.Model):
    hub = models.ForeignKey('Hub',
                            on_delete=models.CASCADE,
                            )
    publish_date = models.DateTimeField()
    name = models.CharField(max_length=200,
                            )
    url = models.URLField()
    author = models.ForeignKey('Author',
                               on_delete=models.RESTRICT,
                               )

    def __str__(self):
        return self.name
