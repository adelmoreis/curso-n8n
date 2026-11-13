/* N8N Academia Agente3d: mapa único do curso.
   Quem lê este arquivo: index.html (simulador) e apostila.html.
   Para mudar nome, número ou ordem de uma missão, edite SÓ aqui.
   Formato de cada item: [chave do progresso (0 = ainda não existe), número, título]. */
window.CURSO={
  key:'n8nAcademiaAgente3d_sim_v1',   /* onde o simulador guarda o progresso do aluno */
  apostila:'apostila.html',
  /* ícones que aparecem no curso e na apostila (mudou aqui, mudou nos dois) */
  icones:{hook:'<svg viewBox="0 0 32 32" fill="none" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="16" cy="8.5" r="3.4" stroke="#ea4b71"/><path d="M14.3 11.7L9.4 20" stroke="#ea4b71"/><circle cx="8" cy="23" r="3.4" stroke="#3b4a57"/><path d="M11.8 23H19" stroke="#3b4a57"/><circle cx="24" cy="23" r="3.4" stroke="#ea4b71"/><path d="M18.5 12.5L22.2 19.4" stroke="#3b4a57"/></svg>'},
  /* texto de boas-vindas: aparece no simulador (1º acesso) e na apostila (Parte 0) */
  intro:{
    oque:'O n8n é uma plataforma para automatizar tarefas conectando aplicativos. Você desenha um fluxo (workflow) com blocos (nodes): quando algo acontece, como um pedido novo, o n8n busca dados, decide o caminho e age, enviando uma mensagem, gravando em uma planilha ou chamando uma IA. Sem você repetir a mesma tarefa na mão.',
    vantagens:['Economiza tempo: tarefas repetitivas passam a rodar sozinhas.','Mais de 1.000 integrações com apps e serviços que você já usa.','É visual: dá para começar sem programar e, quando precisar, usar código.','Pode rodar no seu próprio servidor, com mais controle dos seus dados.','Funciona com IA: dá para montar agentes que leem, decidem e respondem.'],
    tendencia:'Automação com IA é uma das áreas que mais crescem. Segundo a Accel, investidora do n8n (out/2025), a plataforma tem mais de 145 mil estrelas no GitHub e mais de 700 mil desenvolvedores na comunidade, e mais de 80% dos workflows criados nela usam agentes de IA. Quem sabe usar o n8n consegue automatizar processos e entregar resultado rápido para empresas.',
    fonte:{t:'Accel: Our investment in n8n',u:'https://accel.com/news/our-investment-in-n8n-the-ai-platform-for-automation'},
    curso:'Em cada missão o mentor explica, mostra onde clicar e você pratica no simulador. Se errar, ele avisa e dá uma dica. Quando quiser mais detalhes, abra a apostila.'
  },
  /* resumo que abre ao passar no quiz do Mundo 2 (simulador) e aparece no fim do capítulo do projeto (apostila) */
  resumo2:{
    titulo:'O que você aprendeu nos Mundos 1 e 2',
    abre:'Você saiu do zero e agora monta um fluxo completo: o pedido chega sozinho, os dados são organizados, o n8n decide o caminho e busca o que falta. Veja, missão por missão, o que ficou na sua bagagem.',
    mundos:[
      {n:1,t:'Primeiros passos',it:[
        ['1.1 Gatilho e Edit Fields','Todo workflow começa por um gatilho. Cada node tem Input (o que entra), Parameters (o que ele faz) e Output (o que sai), e o mesmo dado pode ser visto em Schema, Table e JSON.'],
        ['1.2 JSON e expressões','Dado é uma ficha com chave e valor. A expressão {{ $json.campo }} busca um dado do node anterior. O ponto entra nas caixas ({{ $json.moto.modelo }}) e, nas listas, a contagem começa do 0.'],
        ['1.3 Tipos de dado','String é texto, Number é número e Boolean é verdadeiro ou falso. A chave Include Other Input Fields mantém o resto do pedido no caminho.']]},
      {n:2,t:'Decisões e dados',it:[
        ['2.1 Webhook','O pedido chega sozinho: Method POST, Path pedido e Listen for test event. Os dados do pedido ficam dentro de body.'],
        ['2.2 HTTP Request e Merge','GET mais uma URL com expressão busca dados na internet (uma API). O HTTP Request devolve só a resposta, então o Merge (Combine e Position) junta de volta com o pedido.'],
        ['2.3 If e Switch','O If faz uma pergunta de sim ou não, com as saídas True e False. O Switch tem várias saídas, uma por regra, e o Fallback pega o que não bateu com nenhuma.'],
        ['2.4 Projeto','Você montou o fluxo inteiro: Webhook, Edit Fields (acerta os tipos), If (o pedido foi pago?) e, no caminho True, o HTTP Request que busca o endereço.']]}
    ],
    fio:'O caminho de quase toda automação é este: receber, organizar, decidir, buscar e juntar. Foi o que você fez com o pedido de Carla Dias, do começo ao fim.',
    erros:'Você também aprendeu a ler os erros mais comuns: 404 (o Webhook não estava escutando ou o Path está diferente), ENOTFOUND, 405 e 400 no HTTP Request, expressão sem as chaves duplas e a diferença entre maiúscula e minúscula.',
    proximo:'No Mundo 3 o pedido continua: você aprende a tratar erros e alertas, repetir tarefas com loops e organizar tudo em sub-workflows. Guarde a apostila: ela é a sua cola.'
  },
  resumo3:{
    titulo:'O que você aprendeu no Mundo 3',
    abre:'No Mundo 2 o fluxo aprendeu a receber, buscar e decidir. No Mundo 3 ele aprendeu a se virar sozinho: avisar quando falha, tratar vários pedidos de uma vez e se organizar em partes reaproveitáveis.',
    mundos:[
      {n:3,t:'Erros, loops e sub-workflows',it:[
        ['3.1 Erros e alertas','Quando um node falha, o workflow para (Stop Workflow). Com On Error em Continue (using error output) o item com problema sai pela saída Error, e ali você liga um aviso no Telegram com {{ $json.body.cliente }} e {{ $json.error }}, para a equipe saber o que aconteceu.'],
        ['3.2 Loop Over Items','O Split Out separa uma lista em itens (body.pedidos virou 3 pedidos). O Loop Over Items entrega um lote por rodada (Batch Size 1), a saída Loop repete os passos e a saída Done entrega tudo no fim. O Wait faz uma pausa de 1 segundo entre as rodadas, para respeitar o limite da API.'],
        ['3.3 Sub-workflows','Um workflow que começa com When Executed by Another Workflow pode ser chamado por outro. Você criou o Buscar CEP e chamou pelo Execute Workflow, sem copiar nodes. Se o endereço mudar, você corrige em um lugar só.']]}
    ],
    fio:'A história do pedido ficou completa: ele chega, é organizado, decidido, buscado e juntado (Mundo 2), e agora também é protegido contra falhas, repetido em lote e dividido em peças que se reaproveitam.',
    erros:'Você aprendeu a reconhecer: o node vermelho que parou o fluxo (Stop Workflow), o erro que passa batido com Continue sem a saída Error, a lista que não foi separada antes do loop, o loop sem a seta de volta e o workflow que não aparece na lista do Execute Workflow porque o sub-workflow ainda não foi criado.',
    proximo:'No Mundo 4 você cria Agentes de IA com ferramentas, memória e saída estruturada, e monta uma automação completa como projeto final. Guarde a apostila: ela é a sua cola.'
  },
  resumo4:{
    titulo:'O que você aprendeu no curso',
    abre:'Você começou com um Edit Fields e terminou com uma automação que decide, pensa e avisa. Este é o resumo do Mundo 4 e do caminho todo.',
    mundos:[
      {n:4,t:'Agentes de IA e projeto final',it:[
        ['4.1 Seu primeiro Agente de IA','O gatilho When chat message received abre um chat de teste. O AI Agent decide sozinho o que fazer, com um Chat Model (o cérebro) e uma System Message. Com o Call n8n Workflow Tool, o sub-workflow Buscar CEP virou ferramenta: o agente lê o nome e a Description para decidir quando usar.'],
        ['4.2 Memória e saída estruturada','Sem memória cada mensagem é uma conversa nova. A Simple Memory, com Context Window Length 5, devolve as últimas mensagens ao agente. Com Require Specific Output Format e o Structured Output Parser, a resposta sai em campos fixos (cliente e mensagem), lidos com {{ $json.output.mensagem }}.'],
        ['4.3 Projeto final','Webhook, If ({{ $json.body.pago }} is true), AI Agent (prompt com {{ $json.body.cliente }} e {{ $json.body.valor }}) e Telegram ({{ $json.output.mensagem }}). Pedido pago envia a confirmação; pedido não pago sai pela saída false e nada acontece.']]}
    ],
    fio:'Mundo 1: ler e tratar dados. Mundo 2: receber, buscar e decidir. Mundo 3: avisar quando falha, repetir em lote e reaproveitar em sub-workflows. Mundo 4: dar inteligência ao fluxo com agentes, que usam o que você já construiu como ferramenta.',
    erros:'Você aprendeu a reconhecer: o agente sem Chat Model (A Chat Model sub-node must be connected and enabled), o agente sem memória que esquece o nome, a ferramenta ignorada por causa de uma Description vaga, o caminho errado para a resposta do agente ($json.mensagem em vez de $json.output.mensagem) e o If sem a expressão $json.body.pago.',
    proximo:'Passe no quiz final, com 12 acertos em 15, para receber o certificado de participação. Depois, guarde a apostila e monte automações para o seu próprio negócio.'
  },
  sumario:[
    {n:1,t:'Primeiros passos',open:true,it:[['m11','1.1','Seu primeiro workflow: gatilho e Edit Fields'],['m12','1.2','O Monstro do JSON: ler dados com expressões'],['m13','1.3','Pedido novo: tratar os dados em sequência'],['q1','Quiz','5 perguntas para fechar o Mundo 1']]},
    {n:2,t:'Decisões e dados',it:[['m21','2.1','Webhooks: o pedido chega sozinho'],['m22','2.2','HTTP Request e Merge: buscar e juntar dados'],['m23','2.3','If e Switch: decidir o caminho'],['m24','2.4','Projeto do Mundo 2: pedido, CEP e decisão'],['q2','Quiz','5 perguntas para fechar o Mundo 2']]},
    {n:3,t:'Erros, loops e sub-workflows',it:[['m31','3.1','Erros e alertas: o fluxo que avisa quando falha'],['m32','3.2','Loop Over Items: vários pedidos, um por vez'],['m33','3.3','Sub-workflows: peças que se reaproveitam'],['q3','Quiz','5 perguntas para fechar o Mundo 3']]},
    {n:4,t:'Agentes de IA e projeto final',it:[['m41','4.1','Seu primeiro Agente de IA: chat, cérebro e ferramenta'],['m42','4.2','Memória e saída estruturada: lembrar e responder em campos'],['m43','4.3','Projeto final: uma automação completa'],['q4','Quiz final','15 perguntas com tudo o que viu. Quem passa recebe o certificado de participação']]}
  ],
  /* qual capítulo da apostila explica cada missão */
  cap:{m11:'c2',m12:'c3',m13:'c4',q1:'c5',m21:'c7',m22:'c8',m23:'c9',m24:'c10',m31:'c11',m32:'c12',m33:'c13',m41:'c14',m42:'c15',m43:'c16'}
};
