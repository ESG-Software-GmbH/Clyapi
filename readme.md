# Clyapi
Clyapi is a python wrapper for the Climcycle api. This allows to perform climcycle ESG analysis in a pythonic way.
So far this repository is a work in progress with only a subset of the Climcycle api implemented. The documentation for 
the full api can be found in the climcycle app documentations tab.

## Setup
### Linux and Mac
Create a virtual environment:
```
python3 -m venv .
```
Activate the virtual environment:
```
source ./bin/activate
```
Install the tool via pip and git:
```
pip install git+https://github.com/ESG-Software-GmbH/Clyapi
```
Create a config files for storing the credentials in the home directory (paste into shell):
```bash
mkdir ~/.clyapi
nano ~/.clyapi/config.json
```
Example config.json:

```json
{
  "Institution_Configs": {
    "Preprod": {
      "Your Institution 1": {
        "Client_Application_Id": "application uuid",
        "Client_Secret": "secret uuid"
      }
    },
    "Prod": {
      "Your Institution 2": {
        "Client_Application_Id": "application uuid",
        "Client_Secret": "secret uuid"
      }
    }
  }
}
```
The institution name can be chosen freely but it is strongly recommended to use the same name as in the climcycle app. 
The Client_Application_Id and the Client_Secret can be found under the Secret Management tab in the Climcycle app, 
given one holds the User Admin role.

## Usage:
Getting started:
```python
import clyapi

client = clyapi.client.Client("Your Institution 1")
print(client)

# test the connection
institution_info = clyapi.endpoints.institution.institution_info(client)
print(institution_info)
```
This code snipped will start an api client and call the institution info endpoint. If it gets a response it means that 
all of the setup steps have been performed correctly.

For exploring the other endpoint wrappers it is suggested to look at the notebooks in the examples folder.
