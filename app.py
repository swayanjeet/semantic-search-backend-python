from flask import Flask
from flask_graphql import GraphQLView

from graphene import ObjectType, String, Schema, List, Int, Field
from JenaQuery import JenaQuery
from flask_cors import CORS

class DataAsset(ObjectType):
    name = String()
    source_environment = String(name='source_environment')
    id = String()
    score = String()
    type = String()
    collection_name = String(name='collection_name')
    object = String()
    object_label = String(name='object_label')
    predicate = String()
    predicate_label = String(name='predicate_label')
    processing_type = String(name='processing_type')
    subject = String()
    subject_label = String(name='subject_label')
    level = Int()
    search_reference = String(name='search_reference')

class DataAssetCollection(ObjectType):
    docs = List(DataAsset)
    numFound = Int()

class Query(ObjectType):
    # this defines a Field `hello` in our Schema with a single Argument `name`

    hello = String(name=String(default_value="stranger"))
    goodbye = String()
    search = Field(DataAssetCollection, q=String(), fq=List(String), page=Int(), size=Int(), depth=Int())
    #search = List(DataAssetCollection)
    # our Resolver method takes the GraphQL context (root, info) as well as
    # Argument (name) for the Field and returns data for the query Response
    def resolve_search(self, info, q, fq, page, size, depth):
        ob1 = JenaQuery(depth, q)
        #print(depth)
        output = ob1.execute_query()
        #print(output)
        docs = []
        for items in output:
            data_asset = DataAsset(name="", source_environment=items["source_environment"], id=items["id"], score=items["score"], type=items["type"], collection_name=items["collection_name"], object=items["object"], object_label=items["object_label"], predicate=items["predicate"], predicate_label=items["predicate_label"], processing_type=items["type"], subject=items["subject"], subject_label=items["subject_label"], level=items["level"], search_reference=items["search_reference"])
            docs.append(data_asset)
        d1 = DataAssetCollection(docs=docs, numFound=len(output))
        print(d1.numFound)
        return d1

    def resolve_hello(root, info, name):
        return f'Hello {name}!'

    def resolve_goodbye(root, info):
        return 'See ya!'

schema = Schema(query=Query)

app = Flask(__name__)
CORS(app)
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

@app.route('/')
def test():
    return "Hello"

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='8082')
