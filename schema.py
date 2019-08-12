from graphene import ObjectType, String, Schema, List, Int, Field

class DataAsset(ObjectType):
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
    search = Field(DataAssetCollection, q=String())
    #search = List(DataAssetCollection)
    # our Resolver method takes the GraphQL context (root, info) as well as
    # Argument (name) for the Field and returns data for the query Response
    def resolve_search(self, info, q):
        #d1 = ["h1","","h2"]
        data_asset = DataAsset(source_environment="Test1", id="1", score="10", type="test_2", collection_name="sample_col", object="Test 2", object_label="Test 3", predicate="Test 4", predicate_label="B", processing_type="A", subject="Z", subject_label="Y", level=1, search_reference="X")
        d1 = DataAssetCollection(docs=[data_asset], numFound=10)
        print(d1.numFound)
        return d1

    def resolve_hello(root, info, name):
        return f'Hello {name}!'

    def resolve_goodbye(root, info):
        return 'See ya!'

schema = Schema(query=Query)

# we can query for our field (with the default argument)
query_string = """
query {
search(q:"Enbrel"){
        numFound
        docs {
            id
        }
    }
}"""
result = schema.execute(query_string)
print(result.data)
