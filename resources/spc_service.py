import requests
import xmltodict

from requests.auth import HTTPBasicAuth
from config import spc_data, body
from copy import deepcopy


SPC = spc_data
login, password, url = SPC["login"], SPC["password"], SPC["uri_consulta"]
headers = {'content-type': 'text/xml'}


def checkSPC(cpf: str = "23693303258") -> dict:
    body_no_cpf = deepcopy(body)
    data = body_no_cpf.replace("CPF_IS_HERE", cpf)
    response = requests.post(url, data=data, headers=headers, auth=HTTPBasicAuth(login, password))
    dict_response = xmltodict.parse(response.content)
    return dict_response
