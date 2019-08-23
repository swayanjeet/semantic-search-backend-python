import json
import requests
import urllib.parse
import re
from math import floor

sample_schema_dict = {
    "source_environment": "semantics_poc",
    "id":"1",
    "score":"",
    "type":"jena_poc",
    "collection_name":"jena_collection",
    "object":"",
    "object_label":"",
    "predicate":"",
    "predicate_label":"",
    "subject":"",
    "subject_label":"",
    "level":"",
    "search_reference":""
}


class JenaQuery:
    query = """
    PREFIX text: <http://jena.apache.org/text#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX base: <http://www.semanticweb.org/am20773/ontologies/2019/7/untitled-ontology-26#>
    SELECT DISTINCT ?subject ?score ?predicate ?object
    FROM <http://35.190.138.34:8080/test/data/sample_graph_1>
    WHERE {
  	{
    VALUES ?predicate { base:hasDerived }
    (?subject ?score) text:query "$$query$$" .
    ?subject ?predicate  ?object .
    }
    UNION
        {
        VALUES ?predicate { base:isDerivedFrom }
        (?subject ?score) text:query "$$query$$" .
        ?subject ?predicate  ?object .
 	    } 
    }
    LIMIT 5
    """
    subjects = []
    ids = []
    output = []
    def __init__(self, depth, query_string):
        self.depth = depth
        self.query_string = query_string
        self.query = self.query.replace("$$query$$",self.query_string)
    
    def execute_sparql_request(self, search_ref=None):
        url = "http://35.190.138.34:8080/test/sparql"
        query_quoted = urllib.parse.quote(self.query)
        payload = "query={}".format(query_quoted)
        headers = {
            'content-type': "application/x-www-form-urlencoded"
            }
        response = requests.request("POST", url, data=payload, headers=headers)
        json_content = json.loads(response.text)
        print(json_content)
        output = []
        string_macthed_subjects = json_content["results"]["bindings"]
        for subject in string_macthed_subjects:
            schema_dict = {
                    "source_environment": "semantics_poc",
                    "id":"1",
                    "score":"",
                    "type":"jena_poc",
                    "collection_name":"jena_collection",
                    "object":"",
                    "object_label":"",
                    "predicate":"",
                    "predicate_label":"",
                    "subject":"",
                    "subject_label":"",
                    "level":"",
                    "search_reference":""
            }
            schema_dict["subject"] = subject["subject"]["value"]
            schema_dict["object"] = subject["object"]["value"]
            schema_dict["predicate"] = subject["predicate"]["value"]
            schema_dict["id"] = schema_dict["subject"]+schema_dict["predicate"]+schema_dict["object"]
            schema_dict["score"] = subject["score"]["value"]
            schema_dict["search_reference"] = search_ref
            schema_dict["level"] = 0
            s_lbl = schema_dict["subject"].split("#")[-1].replace("_"," ")
            schema_dict["subject_label"] = " ".join(re.sub('([a-z])([A-Z])', r'\1 \2', s_lbl).split())
            s_lbl = schema_dict["object"].split("#")[-1].replace("_"," ")
            schema_dict["object_label"] = " ".join(re.sub('([a-z])([A-Z])', r'\1 \2', s_lbl).split())
            s_lbl = schema_dict["predicate"].split("#")[-1].replace("_"," ")
            schema_dict["predicate_label"] = " ".join(re.sub('([a-z])([A-Z])', r'\1 \2', s_lbl).split())
            if schema_dict["predicate"] == "http://www.w3.org/2004/02/skos/core#prefLabel" or schema_dict["predicate"] == "http://www.w3.org/2004/02/skos/core#altLabel":
                schema_dict["predicate_label"] = "has Definition"
                continue
            elif schema_dict["predicate"] == "http://www.w3.org/2004/02/skos/core#definition":
                continue
            if schema_dict["object"] == "https://www.w3.org/2002/07/owl#ObjectProperty" or schema_dict["predicate"] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" or schema_dict["predicate"] == "http://www.w3.org/2000/01/rdf-schema#domain" or schema_dict["object"] == "https://www.w3.org/2002/07/owl#NamedIndividual":
                continue
            else:
                if schema_dict["id"] in self.ids:
                    continue
                else:
                    output.append(schema_dict)
                    self.ids.append(schema_dict["id"])
        return output

    def execute_query(self):
        self.ids=[]
        all_objects = self.execute_sparql_request()
        return all_objects

if __name__ == "__main__":
    ob1 = JenaQuery(1, "Currency")
    print(ob1.execute_query())
