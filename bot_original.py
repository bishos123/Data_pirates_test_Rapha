from urllib.parse import urlencode
from urllib.request import urlopen, Request
import re
from bs4 import BeautifulSoup
import pandas as pd


#input dos dados + check
uf_input_check = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI',
                  'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']

uf_input = str(input('Digite a UF desejada: '))

#inputs e variaveis
while uf_input == uf_input_check:
    uf_input = str(input('Favor escrever apenas a UF! : '))
localidade_input = ''
pagina_ini = -29
pagina_fim = 0
paginas_total = 100
local_cep_pd2 = []
cep_2 = []
local_2 = []
cep_3 = []
local_3 = []
numero_paginas = 0


#começo do loop para paginar o site
while int(pagina_ini) <= int(paginas_total):
    pagina_ini = int(pagina_ini) + 30
    pagina_ini = str(pagina_ini)
    pagina_fim = int(pagina_fim) + 30
    pagina_fim = str(pagina_fim)

    #url e payload
    url = 'https://www2.correios.com.br/sistemas/buscacep/resultadoBuscaFaixaCEP.cfm'
    payload = {'UF': uf_input, 'Localidade': localidade_input, 'pagini' : pagina_ini, 'pagfim' : pagina_fim}

    # function pra limpar string
    def unxml(s):
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        s = s.replace("&amp;", "&")
        s = s.replace("&nbsp;", " ")
        return s

    def unstring(s):
        s = s.replace('\\r', '')
        s = s.replace('\\t', '')
        s = s.replace('\\n', '')
        return s

    # Fazer o request
    request = Request(url, urlencode(payload).encode())
    result = urlopen(request).read()

    #bytes pra str e corrigindo o html
    result = str(result)
    result = unstring(result)
    result = bytes(result, "iso-8859-1").decode("unicode_escape")   #aqui faço virar bytes, pra corrigir e depois volto pra str com decode
    result = unxml(result)

    #Bs4 pra deixar mais especifico
    html = BeautifulSoup(result, 'html.parser')

    #coleta do numero de paginas
    if numero_paginas is not None:
        html_numero_paginas = str(html.select('.ctrlcontent'))
        numero_paginas = str(re.findall(r'Consulta ]</a></div>  (.*?) <br/><br/><table class="tmptabela"', html_numero_paginas))
        numero_paginas = [int(s) for s in re.findall(r'\b\d+\b', numero_paginas)]
        paginas_total = numero_paginas[2]

    #coleta da table
    html_table = str(html.select('.tmptabela'))

    #limpando e encontrando o dado

    html_table = re.sub('\<th>|\<b>|\<th><b>|\<td|\</td>|\</td><td|\</td><|\tr><tr|\</tr><tr>|\</b></th>|\><tr>|\>|\<|\</tr><tr|\/trtr"',"", html_table)
    html_table = re.sub('>Codificado por logradouros</td><td width="85">Total do município</td></tr></table>',"", html_table)
    html_table = re.sub(' width="100"Não codificada por logradouros width="85"Total do município/trtr bgcolor="#C4DEE9"', "", html_table)
    html_table = re.sub('Não codificada por logradouros width="85"Total do município/tr/table', "", html_table)
    html_table = re.sub('codificada por logradouros width="85"Total do município/tr/table', "", html_table)
    html_table = re.sub(' width="100"Codificada por logradouros width="85"Exclusiva da sede urbana/trtr', "", html_table)
    html_table = re.sub(' width="100"Codificada por logradouros width="85"Exclusiva da sede urbana', "", html_table)
    html_table = re.sub(' width="100"Codificado por logradouros width="85"Total do município', "", html_table)
    html_table = re.sub('/trtr bgcolor="#C4DEE9"', "", html_table)
    html_table = re.sub('bgcolor="#C4DEE9"', "", html_table)

    #findall cep
    cep = re.findall(r'width="80"(.*?)width="100', html_table)
    cep = [x.strip() for x in cep] #remover espaços no começo e fim
    cep_3 = cep_3 + cep_2 + cep
    cep_2 = cep

    #findall local
    html_table = re.sub('width="100"Não codificada por logradouros width="85"Total do município', "", html_table) # Tive aqui que limpar por final este texto, pois estava dando erro no ultimo cep que capturava
    local = re.findall(r'width="100"(.*?)width="80"', html_table)
    local_3 = local_3 + local_2 + local
    local_2 = local
    if len(cep) > len(local):
        local_pd = 'invalido'
        local.append(local_pd)
    if len(cep) < len(local):
        cep_pd = 'invalido'
        local.append(cep_pd)


    #pandas e json
    local_cep = {'Local: ': local_3, 'Cep: ' : cep_3}
    print(local_cep)
    local_cep_pd = pd.DataFrame(local_cep)
    local_cep_pd = local_cep_pd.drop_duplicates()
    local_cep_pd = local_cep_pd.to_json(path_or_buf=f'Lista_{uf_input}.json', orient='table',indent=2, force_ascii=False)
    print(local_cep_pd)

