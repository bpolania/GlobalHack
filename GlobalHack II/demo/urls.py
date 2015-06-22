from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^api/ontology/update/$', "demo.views.ontology_update"),
    url(r'^api/ontology/get/$', "demo.views.ontology_get"),
    url(r'^api/ontology/download/$', "demo.views.ontology_download"),
    url(r'^$', "demo.views.index"),
)

