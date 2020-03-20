# Shipchain Common Python Library

A PyPI package containing shared code for ShipChain's Python/Django projects


## Pytest Fixtures

When shipchain-common is installed, a pytest plugin named `json_asserter` is automatically registered.  This plugin is
 designed for writing concise pytest cases that make json_asserter about responses from a Django Rest Framework API. Most 
 of the functionality is tailored to the `application/vnd.api+json` response type, but should still be usable for
 plain `application/json` responses.
 
### json_asserter Fixture

The `json_asserter` fixture exposes several methods for testing specific HTTP Status codes as well as a class for
 building consistent entity references that must be found within the responses.
 
#### Usage with application/vnd.api+json

This is the default when utilizing the `json_asserter`.  If the response does not conform to the 
[JSON Api standard](https://jsonapi.org/), the assertions will fail.
 
##### Asserting Error Responses

To assert that a given response must have an error status, there are several 400-level response methods.  With the
 exception of the HTTP_400 method, each of these include the default error message for ease of use.
 
The following will assert that the response status was 403 and that the default error message ("You do not have
 permission to perform this action") is present.
 
```python
response = api_client.get(self.detail_url)
json_asserter.HTTP_403(response)
```
 
If a different error message should exist, or when checking the error of a 400 response, the specific error may
 be provided as an argument.
 
```python
response = api_client.get(self.detail_url)
json_asserter.HTTP_400(response, error='Specific error message that should be in the respose')
```

##### Asserting Successful Responses

To assert that a given response must have status 200, call the HTTP_200 method with only the Response object:

```python
response = api_client.get(self.detail_url)
json_asserter.HTTP_200(response)
```
 
While this is valid, it is **very strongly** recommended to include additional details about the data present in the
 response. There are two ways to provide the data; however only one way can be used at a time in a given invocation.
 
###### Simple Usage
 
For simple responses, the easiest way to specify required data in the responses is by directly specifying the
 Resource Type `resource`, the Resource Identifier `pk`, as well as any specific Attributes of the resource
  `attributes`. 
  
```python
response = api_client.get(self.detail_url)
json_asserter.HTTP_200(response, 
                    resource='User', 
                    pk='4b56399d-3155-4fe5-ba4a-9718289a78b7', 
                    attributes={'username': 'example_user'})
```

This will throw an assertion if the response is not for the resource type `User` with id 
`4b56399d-3155-4fe5-ba4a-9718289a78b7` and with _at least_ the attribute username `example_user`.  If the response
 includes _additional_ attributes that are not listed in the call to the json_asserter method, they are ignored.  The
 methods check partial objects and do not require that every attribute in the response must be defined in the
 assertion.
   
It is also possible to assert only on the resource type and id without providing attributes.  This is useful if you
 are testing a response that generates content for the fields that may not be known prior to obtaining the response. 
 Additionally, providing only the attributes and not the type and id will check only that an object in the response
 has those attributes, regardless of resource type or id.

###### Advanced Usage
 
For responses where the associated Relationship and any extra Included resources are important, those can be included
 in the assertion.
  
```python
response = api_client.get(self.detail_url)
json_asserter.HTTP_200(response,
                    entity_refs=json_asserter.EntityRef(
                        resource='User', 
                        pk='4b56399d-3155-4fe5-ba4a-9718289a78b7', 
                        attributes={'username': 'example_user'},
                        relationships={
                            'manager': json_asserter.EntityRef( 
                                resource='User', 
                                pk='88e38305-9775-4b34-95d0-4e935bb7156c')}),
                    included=json_asserter.EntityRef(
                        resource='User', 
                        pk='88e38305-9775-4b34-95d0-4e935bb7156c', 
                        attributes={'username': 'manager_user'}))
```

This requires the same original record in the response, but now also requires that there be _at least_ one relationship
 named `manager` with the associated User and that User must be present (with at least the one attribute) in the
 `included` property of the response.
 
The above example utilizes the `EntityRef` exposed via the `json_asserter` fixture.  This is a reference to a single
 entity defined by a combination of: ResourceType, ResourceID, Attributes, and Relationships. When providing the
 `entity_refs` argument to an assertion, you cannot provide any of the following arguments to the assertion directly:
 `resource`, `pk`, `attributes`, or `relationships`.
 
When providing `included` json_asserter, you can provide either a single EntityRef or a list of EntityRef instances.  If
 a list is provided, _all_ referenced entities must be present in the `included` property of the response. As they do
 for the simple usage above, The same assertion rules apply here regarding providing a combination of `resource`, 
 `pk`, and `attributes`.
 
The `entity_refs` parameter can be a list of EntityRef instances as well. However, this is only valid for List
 responses.  If a list of entity_refs is provided for a non-list response, an assertion will occur.  To assert that a
 response is a list, the parameter `is_list=True` must be provided. You can provide either a single EntityRef or a
 list of EntityRef instances.  If a list is provided, _all_ referenced entities must be present in the list of
 returned data.

#### Usage with application/json

Support is included for making assertions on plain JSON responses with `json_asserter`. To ignore the JSON API specific 
 assertions, you must provide the `vnd=False` parameter.  Only the `attributes` parameter is valid as there are no
 relationships or included properties in a plain json response.
 
Given this response:

```json
{
    "id": "07b374c3-ed9b-4811-901a-d0c5d746f16a",
    "name": "example 1",
    "field_1": 1,
    "owner": {
        "username": "user1"
    }
}
```

Asserting the top level attributes as well as nested attributes is possible using the following call:

```python
response = api_client.get(self.detail_url)
json_asserter.HTTP_200(response, 
                    vnd=False,
                    attributes={
                        'id': '07b374c3-ed9b-4811-901a-d0c5d746f16a',
                        'owner': {
                            'username': 'user1'
                        }
                    })
```

For a list response:

```json
[{
    "username": "user1",
    "is_active": False
},
{
    "username": "user2",
    "is_active": False
},
{
    "username": "user3",
    "is_active": False
}]
```

It is possible to assert that one or many sets of attributes exist in the response:
```python
response = api_client.get(self.detail_url)
json_asserter.HTTP_200(response, 
                    vnd=False,
                    is_list=True,
                    attributes=[{
                        "username": "user1",
                        "is_active": False
                    }, {
                        "username": "user3",
                        "is_active": False
                    }])
```

#### Mixin Usage

If there is a class where every test may wish to use the `json_asserter`, than it may be easier to use to the `JsonAsserterMixin` found in `shipchain_common.test_utils`.
This will automatically add the `json_asserter` and set it as a class attribute before the tests are run.
This allows you to just call `self.json_asserter`, allowing for cleaner unit tests imports. 


### HTTPrettyAsserter Usage

When mocking calls, this can help in ensuring all calls, and only those, were made as expected, with the desired parameters.
In order to use, simply import the HTTPrettyAsserter from test_utils and use it in place of the usual httpretty:
```python
@pytest.yield_fixture
def modified_http_pretty():
    HTTPrettyAsserter.enable(allow_net_connect=False)
    yield HTTPrettyAsserter
    HTTPrettyAsserter.disable()
```

Then, you just need to register the uris for the calls you want to mock, and ensure that it is returned in the mocking:
```python
@pytest.fixture
def http_pretty_list_mocking(modified_http_pretty):
    modified_http_pretty.register_uri(modified_http_pretty.POST, 'http://google.com/path', status=status.HTTP_200_OK)
    modified_http_pretty.register_uri(modified_http_pretty.POST, 'http://google.com/other_path',
                                      status=status.HTTP_200_OK)
    modified_http_pretty.register_uri(modified_http_pretty.POST, 'http://bing.com/bing_path',
                                      status=status.HTTP_200_OK)
    return modified_http_pretty
```

In a test that you want to check the calls on, you simply need to use the mocking fixture and call `.assert_calls(assertions)` on the fixture.
These assertions will be a list of details that the call should have made. An example assertion is this:
```python
{
    'path': '/path',
    'body': {
        'integer': 1      
    },
    'query': {
        'query_param_1': 1
    },
    'host': 'google.com',
}
```
 Only the path and the host are required parameters for the assertion. The body and query can be left out, but if included will be tested against.
 If there is a difference between the amount of calls made and the amount of assertions, no assertion will be made and instead an error will return.