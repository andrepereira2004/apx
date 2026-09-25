# Bloqueio, menu Environments e Hytale — 2026-09-13

Pedido: investigar o comportamento das janelas sem o alterar, corrigir o bloqueio
após inatividade e melhorar a primeira abertura de Environments na Quickshell.

## Hytale e Brave: investigação sem alterações

Observações na instalação Hytale:

- Não existe regra Hyprland específica para Hytale ou Brave. As regras gerais
  ignoram pedidos de maximização; a regra de janela única altera apenas a borda.
- `UserData/Settings.json` guarda `Fullscreen: false`, `WindowWidth: 1280` e
  `WindowHeight: 720`. Portanto não há suporte para afirmar que o jogo esteja
  configurado em ecrã inteiro.
- O log `2026-09-13_17-09-34_client.log` regista que o tamanho da janela foi
  corrigido por ultrapassar os limites do ecrã, seguido de tamanho 1280×720.
- No momento da observação, `hyprctl clients -j` mostrava apenas o terminal
  APX HOST ROOT, sem Hytale ou Brave abertos. O terminal estava tiled,
  `fullscreen=0`, com área 1240×634.

Conclusão: não se encontrou uma exceção APX que impeça especificamente Brave de
ficar lado a lado com Hytale. Uma janela flutuante, restrições de tamanho impostas
pelo jogo ou estado de fullscreen durante a execução são hipóteses. A preferência
guardada, por si só, não prova o estado efetivo da janela. É necessário observar
`floating`, `fullscreen`, `fullscreenClient`, workspace e tamanho com os dois
programas abertos para fechar o diagnóstico. Não se abriu o jogo, não se alterou
a sua configuração, nem se mudou qualquer regra ou disposição de janelas.

Referência de semântica: [regras de janelas do Hyprland](https://wiki.hypr.land/0.55.0/Configuring/Basics/Window-Rules/).
A versão/documentação pública não substitui a observação desta instalação.

## Bloqueio: causa confirmada e correção instalada

O journal interno do Hytale regista 14 falhas de autenticação entre 21:15:22 e
21:17:00, todas dirigidas a `user=home`. A alteração anterior de apresentação
introduziu `home` antes de `apx` em `/etc/passwd`, ambos com UID 1000. `home` não
tinha entrada em shadow. Hyprlock resolve a identidade pelo UID antes de iniciar
PAM, conforme o [código upstream](https://github.com/hyprwm/hyprlock/blob/main/src/auth/Pam.cpp).
A password de `apx` continuava inscrita e igual à do Hub; apenas se compararam
valores em memória, sem imprimir ou guardar hashes de credenciais.

Instalado:

- Remoção da entrada duplicada exata nas quatro contas de workload. Todas as
  cinco instalações passam a ter apenas `apx` para UID 1000.
- Launcher e ação de ficheiros conservam `USER=apx`/`LOGNAME=apx`; o alias de pasta
  `/home/Home` e a apresentação Home permanecem. Processos já em execução podem
  conservar variáveis antigas até à próxima entrada; a resolução NSS já foi corrigida.
- O construtor de futuras bases deixa de adicionar o segundo nome de conta.
- O ecrã apresenta uma falha neutra e o indicador distingue autenticação facial
  instalada de autenticação por password. A leitura facial só era configurada
  no Hub: os quatro workloads não têm `pam_howdy.so`. O texto anterior prometia
  uma opção inexistente. Esta correção não instala reconhecimento facial neles.

PAM, passwords, modelos biométricos, contadores de falha e períodos de inatividade
não foram alterados. O registo atual de falhas de `apx` estava vazio. Não se forçou
um bloqueio na sessão do utilizador e não se pediu nem introduziu a password.
O desbloqueio físico continua por confirmar. Há também falhas históricas de
`user=apx` anteriores ao alias, cuja causa não é demonstrada por este diagnóstico.

## Menu: trabalho retirado da primeira abertura

Antes, catálogo, espaço e estado de operações só eram pedidos pelo caminho de
abertura. O catálogo recebido era sempre reatribuído, recriando as linhas e
reiniciando o foco, mesmo com dados iguais.

Agora existe uma pré-leitura assíncrona 250 ms após a descoberta do papel Hub.
Ao abrir, os dados existentes aparecem primeiro e a atualização é pedida após
200 ms, fora da animação de 160 ms. Se a pré-leitura terminar durante a animação,
o novo catálogo aguarda o seu fim. Dados iguais preservam linhas e foco.
Os workloads não executam esta pré-leitura de endpoints Hub. As operações de
criação, remoção e troca continuam a validar o estado atual no Host.

Isto elimina trabalho identificado no caminho inicial, mas não constitui uma
medição do lag após reboot. O Hub estava parado; não se trocou de environment
nem se reiniciou o computador para simular essa situação. A fluidez da primeira
abertura no Hub após arranque/troca permanece aceitação física pendente.

## Validação e recuperação

- 73 testes relevantes passam: catálogo JS executável (4), ficheiros (4),
  componentes/menu (8), promoção de base (6), seed desktop (7), defaults (14),
  troca de environment (24) e manifesto de base (6).
- O novo teste de contas verifica uma única identidade para UID 1000. Testes JS
  executam as funções QML reais para catálogo inalterado, remoção de seleção,
  atualização diferida e recusa da pré-leitura fora do Hub.
- Quickshell ativa recarregou com `Configuration Loaded`. Três ciclos reais de
  abertura/fecho do menu de workload atingiram opacidade 1 e terminaram a animação;
  o menu ficou fechado. Isto não mede frames nem testa o menu completo do Hub.
- Resolução interna de UID devolve `apx` e indicador mostra a instrução de password.
- 37 ficheiros instalados conferem em hash, modo e proprietário; os 55 assets
  do source e 53 assets instalados conferem com os respetivos manifestos.
- Sintaxe de shell, compilação do adaptador e whitespace passam. APX saudável,
  sem unidades Host falhadas, sem rescan de quotas e com 237 GiB disponíveis.
- A tentativa preliminar de carregar QML offscreen foi abandonada: esse backend
  não suporta PanelWindow. Houve primeiro um erro de travessia da pasta temporária,
  corrigido só nessa pasta. Ambas as pastas de teste foram removidas. Um teste
  antigo de mensagem de bloqueio e mocks de ficheiros foram ajustados ao estado
  atual antes da repetição bem-sucedida.

Backup: `/var/lib/apx/backups/20260913T202916Z-lock-menu-repair/`.
`manifest.json` guarda originais, destinos, modos/proprietários e hashes;
`workload-popup-cycles.json` guarda os três ciclos. Para recuperação, restaurar
apenas destinos necessários a partir dos originais, em lugar, com os metadados
registados. Seed e manifestos devem ser restaurados juntos. Repor `/etc/passwd`
reintroduziria o defeito de autenticação; preferir rollback seletivo da UI.
O adaptador datado é evidência desta alteração, não um atualizador geral.
Sem reinício da sessão, instalação de pacotes, commit ou push.
