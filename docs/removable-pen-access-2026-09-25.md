# PEN USB nos Environments com gestor de ficheiros — 2026-09-25

## Objetivo e âmbito

O proprietário pediu acesso à PEN Ventoy no Hytale e nos restantes Environments
com Thunar. A unidade observada é a partição exFAT com UUID `4E21-0000`, num
dispositivo USB amovível. O Hub instalado não tem Thunar. Faculdade, Hytale,
Minecraft e Steam têm o módulo `files` e recebem o atalho «PEN USB».

## Contrato de acesso

O Host valida o UUID, o tipo exFAT, o barramento USB e a marca amovível antes
de montar a partição. Não entrega o dispositivo de blocos ao Environment. Monta
o volume com `nosuid,nodev,noexec` e disponibiliza apenas os ficheiros através
de uma árvore sob o `/run/apx` já partilhado em
`/run/apx/removable-media-v1`. O launcher de cada
Environment gráfico com `files` associa essa árvore a `/media/apx-usb` dentro
do seu espaço de montagem. Um atalho GTK/Thunar mostra «PEN USB» na barra
lateral. O mesmo volume é de leitura e escrita nos quatro Environments, pelo
que as alterações num ficam visíveis nos outros.

O serviço Host observa eventos de dispositivos de blocos. O diretório
partilhado usa propagação de montagens para que a inserção depois do login
também seja visível. Quando a PEN sai, tenta desmontar sem forçar; se algum
processo mantém ficheiros abertos, conserva a montagem até ser possível
desmontar. A reinserção com o mesmo UUID volta a montar a unidade. Não tenta
reparar sistemas de ficheiros e não desmonta montagens de origem desconhecida.

## Riscos e recuperação

Como a mesma PEN é gravável a partir de vários Environments, o isolamento dos
seus ficheiros é deliberadamente relaxado. Só esta identidade física fica
autorizada; outras PENs não são montadas automaticamente. Retirar a unidade
durante uma gravação pode perder dados, como em qualquer volume exFAT. A
operação «Ejetar» do Thunar não se aplica a este atalho de pasta; antes de
retirar, fechar ficheiros e esperar que acabem as cópias.

Para reverter: parar os Environments de trabalho e executar
`deploy-removable-pen-20260925.py --rollback` com o diretório de backup da
instalação. Confirmar que o serviço e a montagem desapareceram. Não formatar
nem alterar a partição. A árvore de montagem em `/run` é recriada após
reinício; a instalação do serviço e do launcher sobrevive.

## Estado

Instalado no piloto físico com backup em
`/var/lib/apx/backups/20260925T170658Z-removable-pen`. O serviço está ativo.
Um teste com o contentor Hytale isolado provou leitura como `apx` e propagação
de desmontagem/remontagem enquanto o contentor continuava aberto. A visualização
em Thunar na sessão gráfica ainda depende da observação do proprietário.
O seed instalado também foi copiado com sucesso por uma execução isolada do
runtime live para simular a criação de um Environment futuro. O digest antigo
do `shell.qml` que bloqueava essa cópia foi alinhado ao ficheiro instalado,
sem mudar o próprio `shell.qml`, com backup em
`/var/lib/apx/backups/20260925T175221Z-future-environment-seed-integrity`.

A primeira instalação foi revertida após criar montagens cobertas por uma
montagem do diretório sobre si mesmo. A versão instalada não faz isso. O Host
retém registos das montagens cobertas anteriores, inacessíveis pelo caminho
atual; verificar a sua eliminação após o próximo reinício. Não desmontar à
força nem alterar a PEN para tentar limpar esses registos.
