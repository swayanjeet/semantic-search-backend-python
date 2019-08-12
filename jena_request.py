import requests
import urllib.parse
import json

url = "http://35.190.138.34:8080/test/sparql"

query = """
PREFIX text: <http://jena.apache.org/text#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?subject ?predicate ?object
FROM <http://35.190.138.34:8080/test/data/semantics_demo>
WHERE {
  ?subject text:query(skos:definition "amgen");
}
"""
query_quoted = urllib.parse.quote(query)

payload = "query={}".format(query_quoted)


headers = {
    'content-type': "application/x-www-form-urlencoded"
    }

response = requests.request("POST", url, data=payload, headers=headers)

json_content = json.loads(response.text)

string_macthed_subjects = json_content["results"]["bindings"]

for subject in string_macthed_subjects:
    print(subject["subject"]["value"])

#print(json_content)
