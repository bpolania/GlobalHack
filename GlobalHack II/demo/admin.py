from django.contrib import admin

from demo.models import Relationship
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('topic', 'userid', 'version', 'name', 'p_rel', 'parent_name', 'created')
    search_fields = ('topic', 'userid', 'version', 'name', 'p_rel', 'parent_name')
admin.site.register(Relationship, RelationshipAdmin)

from demo.models import Ontology
class OntologyAdmin(admin.ModelAdmin):
    list_display = ('topic', 'created', 'userid', 'rationale', 'version')
    search_fields = ('topic', )
admin.site.register(Ontology, OntologyAdmin)