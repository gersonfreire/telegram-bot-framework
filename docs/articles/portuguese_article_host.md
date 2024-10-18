Olá!

O novo framework para Telegram que estamos desenvolvendo já deu seu primeiro filhote utilizável, pelo menos por mim!

Isso porque já utilizei ele para criar o chatbot *HostWatchBot* no telegram, que permite monitorar meus servidores, ou seja, já me atende na minha própria "dor".

Isso tudo está em código fonte aberto no Github, dentro do repositório do Framework e resolvi compartilhar para aqueles que desejam se aprofundar nas vantagens de usar a plataforma Telegram como uma verdadeira "loja de aplicativos", sem gastar nada e sem muita necessidade de esforço de adequação àquelas coisas que só google Play e Apple exigem dos desenvolvedores. Ou seja, seu "app" estará dentro do Telegram na forma de um "bot", de forma rápida e gratuita, sem taxas anuais e com a facilidade de usar qualquer linguagem e até criando "mini-apps" web.

**Segue a descrição de como, em tempo recorde, criei do zero o chatbot de exemplo HostWatch usando o framework que eu mesmo fiz:**

O script *host_monitor_by_user.py* é um  bot escrito a partir do framework  TlgBotFwk, sendo o primeiro exemplo prático de como usar esse framework de forma rápida e simples, usando sua classe base para herdar todos os comandos padrão que, se começássemos do zero na unha, teríamos que implementar. Com isso, o desenvolvedor de bots fica livre para focar somente nas funcionalidades que realmente agregam valor, como neste caso, onde o escopo foi criar um bot do Telegram que fizesse o papel de Watchdog, vigiando servidores que eventualmente caíssem.
Veja o código fonte que ficou bem mais simples, porque só foi necessário implementar o agendamento e a verificação de host on e off usando o "ping".

Com isso o usuário final, com apenas alguns comandos no chatbot, consegue adicionar, excluir ou verificar o andamento das verificações automáticas:

*Para adicionar um host a ser vigiado (onde 60 é o tempo em segundos de intervalo entra verificações de ping): `/addjob host.com.br 60`*

Para chavear o modo de exibição ou não de resultados de verificação positivas: `/togglesuccess`

*Para excluir um host da lista de vigilância, use o comando no chatbot: `/deletejob host.com.br`*

Quando um dos hosts monitorados para de responder a ping, imediatamente o chatbot manda um aviso.

Com isso, pude colocar esse chatbot no ar em tempo recorde e já estou sendo beneficiado por ele para "vigiar" meus servidores, evidentemente esses servidores tem que aceitar responder a ping.

Se você quiser ver o bot ao vivo e a cores já rodando no Telegram, clique no link do bot:

[https://t.me/HostWatchBot](Acessar chatbot HostWatchBot)

Ou vá no Github ver o código fonte, que está na pasta de exemplos do framework:

[https://github.com/gersonfreire/telegram-bot-framework/blob/main/examples/host_monitor_by_user.py]()

Obrigado pela leitura, faça bom uso e se quiser, junte-se a nós nesse empreitada aberta à comunidade!
