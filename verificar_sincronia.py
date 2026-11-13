#!/usr/bin/env python3
"""Confere se o simulador (index.html) e a apostila (apostila.html) estão em dia com o conteudo.js.
Uso: python3 verificar_sincronia.py   (rode a cada mudança no curso)"""
import re,sys,json,subprocess
d=sys.argv[1] if len(sys.argv)>1 else '.'
rd=lambda f:open(d+'/'+f,encoding='utf-8').read()
cj=rd('conteudo.js');ix=rd('index.html');ap=rd('apostila.html')
node=subprocess.run(['node','-e',"global.window={};eval(require('fs').readFileSync('%s/conteudo.js','utf8'));console.log(JSON.stringify(window.CURSO))"%d],capture_output=True,text=True)
C=json.loads(node.stdout);erros=[]
chs=set(re.findall(r"chapter\('(c\d+)'",ap))
for w in C['sumario']:
    for key,num,t in w['it']:
        if not key: continue
        if re.match(r'\d',num):
            cap=C['cap'].get(key)
            if not cap: erros.append('Missão %s (%s) sem capítulo da apostila em cap'%(num,t))
            elif cap not in chs: erros.append('Missão %s aponta para %s, que não existe na apostila'%(num,cap))
            if "'"+key+"'" not in ix: erros.append('Missão %s: chave %s não aparece no simulador'%(num,key))
# fatos que o aluno digita ou vê: precisam estar no simulador E na apostila
fatos=['viacep.com.br/ws/','body.pago','body.pagamento','Carla Dias','40010000','Listen for test event','Combine','Position','Fallback','is true','cartao','Execute step','pedido','$json.pago','body.valor','Include Other Input Fields','Boolean','Number','resumo2','resumo3','Continue (using error output)','On Error','123456789','body.pedidos','Batch Size','Execute Workflow','When Executed by Another Workflow','Buscar CEP','Split Out','Loop Over Items','Wait Amount','Telegram','resumo4','AI Agent','Chat Model','Simple Memory','Structured Output Parser','Call n8n Workflow Tool','Context Window Length','Require Specific Output Format','$json.output.mensagem','When chat message received']
for f in fatos:
    if f not in ix: erros.append('Simulador não tem: '+f)
    if f not in ap: erros.append('Apostila não tem: '+f)
for t in ['Webhook','HTTP Request','If','Switch','Merge','Edit Fields','Split Out','Loop Over Items','Wait','Telegram','Execute Workflow','AI Agent','Simple Memory','Structured Output Parser']:
    if t not in ap: erros.append('Apostila não explica o node '+t)
for t in ['intro']:
    if 'CURSO.'+t not in ix: erros.append('Simulador não usa o texto de boas-vindas do conteudo.js')
    if 'CURSO.'+t not in ap and '(window.CURSO&&CURSO.'+t not in ap: erros.append('Apostila não usa o texto de boas-vindas do conteudo.js')
import re as _re
for _n,_t in (('apostila',ap),('conteudo.js',open('conteudo.js',encoding='utf-8').read())):
    if _re.search(r'painel|gestor|pagamento do aluno|cobran',_t,_re.I): erros.append('A '+_n+' cita a area do gestor, e isso nao pode aparecer no material do aluno')
print('SINCRONIA OK' if not erros else 'FALTA ATUALIZAR:\n- '+'\n- '.join(erros))
sys.exit(1 if erros else 0)
