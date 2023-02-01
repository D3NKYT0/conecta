import requests
import xmltodict

from requests.auth import HTTPBasicAuth
from config import spc_data


SPC = spc_data
login, password, url = SPC["login"], SPC["password"], SPC["uri_consulta"]

body = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:web="http://webservice.consulta.spcjava.spcbrasil.org/">
<soapenv:Header/>
<soapenv:Body>
<web:filtro>
<codigo-produto>13</codigo-produto>
<tipo-consumidor>F</tipo-consumidor>
<documento-consumidor>23693303258</documento-consumidor>
<cep-consumidor>04302010</cep-consumidor>
<telefone-consultar>
<ddd>19</ddd>
<numero>36562854</numero>
</telefone-consultar>
<utiliza-CMC7>true</utiliza-CMC7>
<cmc71-cheque-inicial>34116857</cmc71-cheque-inicial>
<cmc72-cheque-inicial>0010000015</cmc72-cheque-inicial>
<cmc73-cheque-inicial>500001381151</cmc73-cheque-inicial>
<quantidade-cheque>1</quantidade-cheque>
<cheque-detalhado>
<numero>1</numero>
<digito>9</digito>
<data-deposito>2023-02-01T00:00:00.000-02:00</data-deposito>
<valor>1.00</valor>
</cheque-detalhado>
<cep-origem>04302010</cep-origem>
<codigo-estacao-consultante>FFF</codigo-estacao-consultante>
<data-nascimento-rg>1960-06-15T00:00:00</data-nascimento-rg>
</web:filtro>
</soapenv:Body>
</soapenv:Envelope>
"""

headers = {'content-type': 'text/xml'}
headers['SOAPAction'] = "listarProdutos"
response = requests.post(url, data=body, headers=headers, auth=HTTPBasicAuth(login, password))
to_dict = xmltodict.parse(response.content)

print(to_dict)
