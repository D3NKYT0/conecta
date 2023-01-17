import base64
import logging
import requests
import xmltodict


def get_spc_cpf(login: str, password: str):
    try:
        body = """
        """
        authorization = base64.b64encode(f'{login}:{password}'.encode('utf-8'))
        headers = {"Authorization": f"Basic {authorization}", "Content-Type": "application/xml"}
        url = "https://servicos.spc.org.br/spc/remoting/ws/consulta/buscaWebService"
        response = requests.post(url, headers=headers, data=body, timeout=10.0)
        return response
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise logging.error('Servidor fora do ar!')

response = get_spc_cpf("2357720", "Recife147")
converted = response.content
dict_converted = xmltodict.parse(converted)
print(dict_converted)
