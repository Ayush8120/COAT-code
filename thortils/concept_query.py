import requests
import sys
'''
Beware conceptnet is case sensitive
'''
def query_conceptnet(concepts):
    '''
    takes object names and returns 
    '''
    # print("Hi Welcome To ConceptNet!!")
    results = []
    for concept in concepts:
        
        base_url = 'http://api.conceptnet.io'
        search_endpoint = '/query'
        
        # Build the URL for the API request
        # url = f"{base_url}{search_endpoint}?start=/c/en/{concept}&limit=500"
        url2 =f"{base_url}{search_endpoint}?start=/c/en/{concept}&rel=/r/UsedFor&limit=1"

        try:
            # Send the GET request to ConceptNet API
            response = requests.get(url2)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the response as JSON
                data = response.json()
                # Extract and return the edges from the response
                if 'edges' in data and len(data['edges']) != 0:
                    results.append([data['edges']])  
                elif 'edges' in data and len(data['edges']) == 0:
                    url2 =f"{base_url}{search_endpoint}?start=/c/en/{concept}&rel=/r/CapableOf&limit=1"
                    response = requests.get(url2)
                    data = response.json()
                    if 'edges' in data and len(data['edges']) != 0:
                        results.append([data['edges']])
                    else:
                        url2 =f"{base_url}{search_endpoint}?start=/c/en/{concept}&rel=/r/ReceivesAction&limit=1"
                        response = requests.get(url2)
                        data = response.json()
                        if 'edges' in data and len(data['edges']) != 0:
                            results.append([data['edges']])
                        else:
                            print("No Edge for any of the 3 relations and that object")
                            results.append([[]])
            else:
                print(f"Error: Unable to query ConceptNet. Status Code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
    return results

# Example usage:
concept_to_query = ["lettuce","mug"]
results = query_conceptnet(concept_to_query)
print(results)

# if results:
#     print(f"Results for {concept_to_query}:")
#     print(len(results))
#     for i,result in enumerate(results):
#         for edge in result:
#             # if edge['rel']['label'] == 'UsedFor':
#             print(edge)
#             print('YO')
#             if edge != []:
#                 print(edge)
#                 print(f"{edge[0]['start']['label']} --{edge[0]['rel']['label']}--> {edge[0]['end']['label']}")
# else:
#     print("No results found.")
    
