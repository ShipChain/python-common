# shipchain-common
A PyPI package containing shared code for ShipChain's Python/Django projects


### Pytest Fixtures

When shipchain-common is installed, a pytest plugin named `assertions` is automatically registered.  This plugin is
 designed for writing concise pytest cases that make assertions about responses from a Django Rest Framework API. Most 
 of the functionality is tailored to the `application/vnd.api+json` response type, but should still be usable for
 plain `application/json` responses.
 
#### Assertions Fixture

The `assertions` fixture exposes several methods for testing specific HTTP Status codes as well as a class for
 building consistent entity references that must be found within the responses.
 
##### Asserting Error Responses

To assert that a given response must have an error status, there are several 400-level response methods.  With the
 exception of the HTTP_400 method, each of these include the default error message for ease of use.
 
The following will assert that the response status was 403 and that the default error message ("You do not have
 permission to perform this action") is present.
 
```python
response = api_client.get(self.detail_url)
assertions.HTTP_403(response)
```
 
If a different error message should exist, or when checking the error of a 400 response, the specific error may
 be provided as an argument.
 
```python
response = api_client.get(self.detail_url)
assertions.HTTP_400(response, error='Specific error message that should be in the respose')
```

##### Asserting Successful Responses

To assert that a given response must have status 200, call the HTTP_200 method with only the Response object:

```python
response = api_client.get(self.detail_url)
assertions.HTTP_200(response)
```
 
While this is valid, it is **very strongly** recommended to include additional details about the data present in the
 response. There are two ways to provide the data; however only one way can be used at a time in a given invocation.
 
###### Simple Usage
 
For simple responses, the easiest way to specify required data in the responses is by directly specifying the
 Resource Type `resource`, the Resource Identifier `pk`, as well as any specific Attributes of the resource
  `attributes`. 
  
```python
response = api_client.get(self.detail_url)
assertions.HTTP_200(response, 
                    resource='User', 
                    pk='4b56399d-3155-4fe5-ba4a-9718289a78b7', 
                    attributes={'username': 'example_user'})
```

This will throw an assertion if the response is not for the resource type `User` with id 
`4b56399d-3155-4fe5-ba4a-9718289a78b7` and with _at least_ the attribute username `example_user`.  If the response
 includes _additional_ attributes that are not listed in the call to the assertions method, they are ignored.  The
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
assertions.HTTP_200(response,
                    entity_refs=assertions.EntityRef(
                        resource='User', 
                        pk='4b56399d-3155-4fe5-ba4a-9718289a78b7', 
                        attributes={'username': 'example_user'},
                        relationships={
                            'manager': assertions.EntityRef( 
                                resource='User', 
                                pk='88e38305-9775-4b34-95d0-4e935bb7156c')}),
                    included=assertions.EntityRef(
                        resource='User', 
                        pk='88e38305-9775-4b34-95d0-4e935bb7156c', 
                        attributes={'username': 'manager_user'}))
```

This requires the same original record in the response, but now also requires that there be _at least_ one relationship
 named `manager` with the associated User and that User must be present (with at least the one attribute) in the
 `included` property of the response.
 
The above example utilizes the `EntityRef` exposed via the `assertions` fixture.  This is a reference to a single
 entity defined by a combination of: ResourceType, ResourceID, Attributes, and Relationships. When providing the
 `entity_refs` argument to an assertion, you cannot provide any of the following arguments to the assertion directly:
 `resource`, `pk`, `attributes`, or `relationships`.
 
When providing `included` assertions, you can provide either a single EntityRef or a list of EntityRef instances.  If
 a list is provided, _all_ referenced entities must be present in the `included` property of the response. As they do
 for the simple usage above, The same assertion rules apply here regarding providing a combination of `resource`, 
 `pk`, and `attributes`.
 
The `entity_refs` parameter can be a list of EntityRef instances as well. However, this is only valid for List
 responses.  If a list of entity_refs is provided for a non-list response, an assertion will occur.  To assert that a
 response is a list, the parameter `is_list=True` must be provided. You can provide either a single EntityRef or a
 list of EntityRef instances.  If a list is provided, _all_ referenced entities must be present in the list of
 returned data.
