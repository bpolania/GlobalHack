from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
from demo.models import Relationship, Ontology
import hashlib
import datetime
#from processor import ontology

@csrf_exempt
def index(request):

    return render(request, 'index.html', {
        "results": {}
    })

@csrf_exempt
def ontology_download(request):
    dl_format = request.POST['dl_format']
    topic = request.POST['topic']
    ont_data = json.loads(request.POST['ontology'])
    if dl_format == "flatjson":
        ont_data = _to_db_format(topic, 0, 0, "", [ont_data])
        results = json.dumps(ont_data, indent=4)
        extension = ".json"
    elif dl_format == "treejson":
        results = json.dumps(ont_data, indent=4)
        extension = ".json"
    else:
        ont_data = _to_db_format(topic, 0, 0, "", [ont_data])
        results = _json_to_owl(ont_data)
        extension = ".owl"
    response = HttpResponse(results, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="'+topic+'_'+datetime.datetime.now().isoformat()[:19]+'.'+extension+'"'
    return response

@csrf_exempt
def ontology_update(request):
    topic = request.POST['topic']
    userid = 1
    version = 1 #default
    ont_data = json.loads(request.POST['ontology'])
    rationale = request.POST['rationale']
    existing_ont_by_user = Ontology.objects.filter(topic=topic, userid=userid).order_by("-version")
    if existing_ont_by_user:
        version = existing_ont_by_user[0].version + 1
    o = Ontology(**{
        "topic":topic,
        "userid":userid,
        "version": version,
        "rationale":rationale
    })
    o.save()

    db_values = _to_db_format(topic, userid, version, "", [ont_data])
    Relationship.objects.bulk_create([Relationship(**x) for x in db_values])

    versions = []
    for o in Ontology.objects.filter(topic=topic, userid=1).order_by("-version"):
        versions.append({
            "version": o.version,
            "rationale": o.rationale,
            "id": o.id,
            "created": o.created.isoformat()
        })

    return HttpResponse(json.dumps({'ontology':ont_data, 'versions':versions}), content_type='application/json')

@csrf_exempt
def ontology_get(request):
    topic = request.POST['topic'].strip()
    userid = request.POST['userid'].strip()
    if userid == "-1":
        version = 0
    elif 'version' in request.POST:
        version = int(request.POST['version'])
    else:
        version = 0
        try:
            print 1
            ex_ont = Ontology.objects.filter(topic=topic, userid=userid).order_by("-version")[0]
            version = ex_ont.version
        except:
            if userid != 0:
                print 2
                try:
                    print 4
                    Ontology.objects.get(topic=topic, userid=0)
                    userid = 0
                except:
                    print 5
                    _create_ontology(topic)
                    userid = 0
            else:
                print 3
                _create_ontology(topic)
                userid = 0

    if userid == "-1":
        #get collaborative/crowdsourced version
        big_dict = {}
        big_lookup = {}
        rel_data = Relationship.objects.serialize(Relationship.objects.filter(topic=topic))
        for r in rel_data:
            if r['name'] not in big_dict:
                big_dict[r['name']] = {}
            if r['parent_name']+"|"+r['p_rel'] not in big_dict[r['name']]:
                big_dict[r['name']][r['parent_name']+"|"+r['p_rel']] = 1
            else:
                big_dict[r['name']][r['parent_name']+"|"+r['p_rel']] += 1
            big_lookup[r['name']+"|"+r['parent_name']+"|"+r['p_rel']] = r

        final_data = []
        for name in big_dict:
            best_option = ""
            best_value = 0
            for option,value in big_dict[name].items():
                if value > best_value:
                    best_value = value
                    best_option = option
            final_data.append(big_lookup[name+"|"+best_option])
        rel_data = final_data
    else:
        print "h"
        rel_data = Relationship.objects.serialize(Relationship.objects.filter(topic=topic, userid=userid, version=version))

    print "f"
    hierarchy_data = _from_db_format("", rel_data)

    print "a"
    versions = []
    for o in Ontology.objects.filter(topic=topic, userid=1).order_by("-version"):
        versions.append({
            "version": o.version,
            "rationale": o.rationale,
            "id": o.id,
            "created": o.created.isoformat()
        })
    print "b"
        
    return HttpResponse(json.dumps({'ontology':hierarchy_data, 'versions':versions}), content_type='application/json')

def _json_to_owl(db_values):
    unique_topic = hashlib.md5(db_values[0]['topic']).hexdigest()
    xml = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
     xml:base="http://127.0.0.1:8000/ontology/"""+unique_topic+""""
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:xml="http://www.w3.org/XML/1998/namespace"
     ontologyIRI="http://127.0.0.1:8000/ontology/"""+unique_topic+"""">
    <Prefix name="rdf" IRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#"/>
    <Prefix name="rdfs" IRI="http://www.w3.org/2000/01/rdf-schema#"/>
    <Prefix name="xsd" IRI="http://www.w3.org/2001/XMLSchema#"/>
    <Prefix name="owl" IRI="http://www.w3.org/2002/07/owl#"/>"""
    Declaration = []
    SubClassOf = []
    AnnotationAssertion = []
    for d in db_values:
        unique_id = hashlib.md5(d['topic']+"|"+d['name']+"|"+str(d['userid'])+"|"+str(d['version'])).hexdigest()
        parent_unique_id = hashlib.md5(d['topic']+"|"+d['parent_name']+"|"+str(d['userid'])+"|"+str(d['version'])).hexdigest()
        Declaration.append("""
    <Declaration>
        <Class IRI="http://127.0.0.1:8000/node/"""+unique_id+""""/>
    </Declaration>""")
        SubClassOf.append("""
    <SubClassOf>
        <Class IRI="http://127.0.0.1:8000/node/"""+unique_id+""""/>
        <Class IRI="http://127.0.0.1:8000/node/"""+parent_unique_id+""""/>
    </SubClassOf>""")
        AnnotationAssertion.append("""
    <AnnotationAssertion>
        <AnnotationProperty abbreviatedIRI="rdfs:label"/>
        <IRI>http://127.0.0.1:8000/node/"""+unique_id+"""</IRI>
        <Literal datatypeIRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#PlainLiteral">"""+d['name']+"""</Literal>
    </AnnotationAssertion>""")

    xml += "".join(Declaration)
    xml += "".join(SubClassOf)
    xml += "".join(AnnotationAssertion)

    xml += """
</Ontology>
    """
    return xml


def _create_ontology(topic):
    print "_create_ontology"

    o = Ontology(**{
        "topic":topic,
        "userid":0,
        "version": 0,
        "rationale":'Base'
    })
    o.save()
    
    #ont_data = fake_data(topic)
    #db_values = _to_db_format(topic, 0, 0, "", [ont_data])
    #Relationship.objects.filter(topic=topic).delete()
    #Relationship.objects.bulk_create([Relationship(**x) for x in db_values])

    ont_data = Relationship.objects.serialize(Relationship.objects.filter(topic=topic))
    ont_data = _from_db_format("", ont_data)

    return ont_data

def _from_db_format(parent_name, data):
    db_values = []
    #This doesn't scale well, need to revamp
    for o in data:
        if o['parent_name'] == parent_name:
            db_values.append({
                "name": o['name'],
                "p_rel": o['p_rel'],
                "children": _from_db_format(o['name'], data) #recurrrrrrsion
            })
    if parent_name == "" and len(db_values) > 0:
        db_values = db_values[0]
    return db_values

def _to_db_format(topic, userid, version, parent_name, data):
    db_values = []
    for o in data:
        db_values.append({
            "topic": topic,
            "userid": userid,
            "version": version,
            "name": o['name'],
            "p_rel": o['p_rel'],
            "parent_name": parent_name
        })
        if 'children' in o and len(o['children']) > 0:
            db_values.extend(_to_db_format(topic, userid, version, o['name'], o['children'])) #ooooooh snaps!
    return db_values

def fake_data(topic):
    return {
        "name": topic, #"biological process"
        "p_rel": "",
        "children": [
            {
                "name": "physiological process",
                "p_rel": "is_a",
                "children": [
                    {
                        "name": "cell cycle",
                        "p_rel": "is_a",
                        "children": [
                            {
                                "name": "M Phase",
                                "p_rel": "part_of",
                                "children": [ ]
                            },
                            {
                                "name": "meiotic cell cycle",
                                "p_rel": "is_a",
                                "children": [ ]
                            },
                        ]
                    },

                ]
            },
            {
                "name": "cellular process",
                "p_rel": "is_a",
                "children": [
                    {
                        "name": "cell division",
                        "p_rel": "is_a",
                        "children": [
                            {
                                "name": "cytokinesis",
                                "p_rel": "is_a",
                                "children": [ ]
                            },
                        ]
                    },
                ]
            },
        ]
    }


def fake_data2(topic):
    return {
        "name": topic, #"pizza"
        "p_rel": "",
        "children": [
            {
                "name": "Crust",
                "p_rel": "ingredient",
                "children": [
                    {
                        "name": "thin crust",
                        "p_rel": "is_a",
                        "children": [
                            {
                                "name": "St. Louis style",
                                "p_rel": "includes",
                                "children": [ ]
                            },
                            {
                                "name": "New York style",
                                "p_rel": "includes",
                                "children": [ ]
                            },
                        ]
                    },
{
                        "name": "thick crust",
                        "p_rel": "is_a",
                        "children": [
                            {
                                "name": "Chicago style",
                                "p_rel": "includes",
                                "children": [ ]
                            },
                        ]
                    },

                ]
            },
            

            {
                "name": "City Style",
                "p_rel": "style_of",
                "children": [
                    {
                        "name": "St. Louis style",
                        "p_rel": "is_a",
                        "children": [
                            {
                                "name": "thin crust",
                                "p_rel": "ingredient",
                                "children": [ ]
                            },
                            {
                                "name": "Provel cheese",
                                "p_rel": "ingredient",
                                "children": [ ]
                            },
                            {
                                "name": "sauce on bottom",
                                "p_rel": "layering_method",
                                "children": [ ]
                            },

                        ]
                    },
                    {
                        "name": "Chicago style",
                        "p_rel": "is_a",
                        "children": [
                            {
                                "name": "thick crust",
                                "p_rel": "ingredient",
                                "children": [ ]
                            },
                            {
                                "name": "Mozzarella cheese",
                                "p_rel": "ingredient",
                                "children": [ ]
                            },
                            {
                                "name": "sauce on top",
                                "p_rel": "layering_method",
                                "children": [ ]
                            },

                        ]
                    },
                    {
                        "name": "New York style",
                        "p_rel": "is_a",
                        "children": [
                            {
                                "name": "thin crust",
                                "p_rel": "ingredient",
                                "children": [ ]
                            },
                            {
                                "name": "Mozzarella cheese",
                                "p_rel": "ingredient",
                                "children": [ ]
                            },
                            {
                                "name": "sauce on bottom",
                                "p_rel": "layering_method",
                                "children": [ ]
                            },

                        ]
                    },

                ]
            },
            
            {
                "name": "Cheese",
                "p_rel": "ingredient",
                "children": [
                    {
                        "name": "Provel",
                        "p_rel": "is_a",
                        "children": [
                            {
                                "name": "St. Louis style",
                                "p_rel": "includes",
                                "children": [ ]
                            },

                        ]
                    },
                    {
                        "name": "Mozzarella",
                        "p_rel": "is_a",
                        "children": [
                            {
                                "name": "Chicago style",
                                "p_rel": "includes",
                                "children": [ ]
                            },
                            {
                                "name": "New York style",
                                "p_rel": "includes",
                                "children": [ ]
                            },

                        ]
                    },

                ]
            },

        ]
    }


def json_custom_parser(obj):
    """
        A custom json parser to handle json.dumps calls properly for Decimal and Datetime data types.
    """
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        dot_ix = 19 # 'YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM'.find('.')
        return obj.isoformat()[:dot_ix]
    else:
        raise TypeError
