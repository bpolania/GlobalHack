from django.db import models
import json
import datetime
from decimal import Decimal

class GeneralManager(models.Manager):
    def serialize(self, data):
        return list(data.values())

    def jsonify(self, data, serialize=True, indent=None):
        if serialize:
            data = self.serialize(data)
        return json.dumps(data, default=json_custom_parser, indent=indent)

class Ontology(models.Model):
    objects = GeneralManager()
    topic = models.CharField(max_length=255)
    userid = models.CharField(max_length=255) #0 = base, -1 = crowdsourced
    rationale = models.CharField(max_length=255)
    version = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.topic)

    class Meta:
        verbose_name = 'Ontology'
        verbose_name_plural = 'Ontologies'
        app_label = "demo"

class Relationship(models.Model):
    objects = GeneralManager()

    topic = models.CharField(max_length=255)
    userid = models.CharField(max_length=255) #0 = base, -1 = crowdsourced
    version = models.IntegerField(default=0)

    name = models.CharField(max_length=255) #current node
    p_rel = models.CharField(max_length=255) #is_a
    parent_name = models.CharField(max_length=255) #parent node

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.topic)

    class Meta:
        verbose_name = 'Relationship'
        verbose_name_plural = 'Relationships'
        app_label = "demo"

def json_custom_parser(obj):
    """
        A custom json parser to handle json.dumps calls properly for Decimal and Datetime data types.
    """
    if isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        dot_ix = 19 # 'YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM'.find('.')
        return obj.isoformat()[:dot_ix]
    else:
        raise TypeError