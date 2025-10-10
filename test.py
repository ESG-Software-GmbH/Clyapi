import clyapi

client = clyapi.client.Client()


institution_info = clyapi.endpoints.institution.institution_info(client)
print(institution_info)