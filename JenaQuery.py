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
    query_level_0 = """
    PREFIX text: <http://jena.apache.org/text#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT ?subject ?score
    FROM <http://35.190.138.34:8080/test/data/semantics_demo>
    WHERE {
    (?subject ?score) text:query (skos:definition "$$query_string$$");
    }
    LIMIT 5
    """
    query_level_1_as_subject = """
    PREFIX text: <http://jena.apache.org/text#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT ?subject ?predicate ?object
    FROM <http://35.190.138.34:8080/test/data/semantics_demo>
    WHERE {
    VALUES ?subject { <$$subject$$> }
    ?subject ?predicate ?object
    }
    LIMIT 10
    """
    query_level_1_as_object = """
    PREFIX text: <http://jena.apache.org/text#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT ?subject ?predicate ?object
    FROM <http://35.190.138.34:8080/test/data/semantics_demo>
    WHERE {
    VALUES ?object { <$$object$$> }
    ?subject ?predicate ?object
    }
    LIMIT 10
    """
    def __init__(self, depth, query_string):
        #print(depth, "init called")
        self.depth = depth
        self.query_string = query_string
        self.ids = []
        
    def form_query(self, curr_depth, output_dict=None):
        if curr_depth == -1:
            self.query = self.query_level_0.replace("$$query_string$$",self.query_string)
        elif curr_depth == 0:
            self.query = {}
            for subject in output_dict:
                self.query[subject["subject"]] = {"queries": [self.query_level_1_as_subject.replace("$$subject$$", subject["subject"]),
                self.query_level_1_as_object.replace("$$object$$", subject["subject"])], "score":subject["score"] }
        else:
            self.query = {}
            for subject in output_dict:
                self.query[subject["object"]] = {"queries": [self.query_level_1_as_subject.replace("$$subject$$", subject["object"]),
                self.query_level_1_as_object.replace("$$object$$", subject["object"])], "score":subject["score"] }
    
    def execute_sparql_request(self, query, depth, score=None, search_ref=None):
        url = "http://35.190.138.34:8080/test/sparql"
        query_quoted = urllib.parse.quote(query)
        payload = "query={}".format(query_quoted)
        headers = {
            'content-type': "application/x-www-form-urlencoded"
            }
        response = requests.request("POST", url, data=payload, headers=headers)
        json_content = json.loads(response.text)
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
            if depth == -1:
                schema_dict["subject"] = subject["subject"]["value"]
                schema_dict["score"] = subject["score"]["value"]
                output.append(schema_dict)
            else:
                schema_dict["subject"] = subject["subject"]["value"]
                schema_dict["object"] = subject["object"]["value"]
                schema_dict["predicate"] = subject["predicate"]["value"]
                schema_dict["id"] = schema_dict["subject"]+schema_dict["predicate"]+schema_dict["object"]
                schema_dict["score"] = score
                schema_dict["search_reference"] = search_ref
                schema_dict["level"] = depth
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
        all_objects = []
        self.form_query(-1)
        output = self.execute_sparql_request(self.query, -1)
        #print(output)

        for i in range(0, self.depth+1):
            self.form_query(i, output)
            output = []
            #print(self.query)
            for subject, query_dict in self.query.items():
                for query in query_dict["queries"]:
                    #print(query)
                    output += self.execute_sparql_request(query, i, query_dict["score"], subject)
                    #print(output)
            all_objects+=output
            #print(all_objects)
        #     i+=1
        #print(self.ids)
        return all_objects

if __name__ == "__main__":
    ob1 = JenaQuery(1, "amgen")
    print(ob1.execute_query())
