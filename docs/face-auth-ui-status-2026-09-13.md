# Ecrã de autenticação e mensagens faciais — 2026-09-13

O utilizador pediu uma apresentação atual e mensagens coerentes com a atividade
real. A alteração está instalada nas cinco configurações de bloqueio e no seed
independente. O reconhecimento facial continua exclusivamente no Hub.

## Correções

O aspeto usa agora texto branco/cinzento, Adwaita Mono, título em caixa normal,
campo neutro de 380×56 com cantos de 10px e borda fina. A indicação de validação
é genérica (`A autenticar…`), sem afirmar que a câmara está ativa. Falhas são
indicadas apenas pelo campo controlado pelo PAM/Hyprlock. O layout de teclado
real aparece abaixo do campo, útil para a recuperação por password. Fundo opaco
preservado, sem exposição do conteúdo da sessão bloqueada.

Antes, o indicador procurava qualquer marcador Howdy vivo na sessão, incluindo
uma verificação iniciada por outro programa. Sem marcador, anunciava `APÓS FALHA`
mesmo sem evidência de falha. Também bastava ter recebido uma única imagem para
continuar a anunciar captura durante todo o processo.

O novo helper Python:

- verifica módulo, modelo legível, configuração PAM e `disabled=false`;
- encontra o Hyprlock que iniciou o helper, seguindo os processos pais;
- considera apenas comparações Howdy descendentes desse mesmo PID/início;
- distingue preparação, receção recente de imagem e espera por nova imagem;
- valida nome exato do programa, PID/início, ficheiro regular, proprietário e
  modo privado do marcador; marcadores de processos mortos/reutilizados e de
  outras tentativas não comandam a mensagem;
- sem tentativa ativa, apresenta instruções neutras de password/Enter, sem
  inferir sucesso, falha, timeout ou câmara tapada.

Howdy atualiza o marcador no máximo quatro vezes por segundo, apenas depois de
`read_frame()` devolver imagem. Após dois segundos sem atualização, o indicador
passa de procura de rosto a espera por imagem. O ciclo visual consulta a cada
300 ms; portanto não se promete sincronização instantânea nem confirmação de
correspondência facial por mera captura. O helper não autentica nem lê modelos
ou passwords. O marcador é apenas apresentação e nunca autoriza desbloqueio.
Falhas ao publicar/limpar o marcador não fazem falhar PAM.

Não se alteraram PAM, passwords, modelos, tolerâncias de reconhecimento, duração
da procura, dispositivos, entrada inicial, regras de falhas ou a via de password.
O novo campo não mostra pormenores de erro do PAM; apresenta falha genérica.

## Evidência e limites

39 testes relevantes passam: estados/heartbeat (12), defaults (14), seed desktop
(7) e base (6). Incluem separação entre tentativas, reutilização de PID, processo
morto, ficheiro simbólico, captura sem imagem recente, parentesco com nomes que
contêm parênteses e falhas de escrita que não interrompem autenticação.

A configuração candidata foi carregada pelo Hyprlock real num compositor de
teste separado. Inspeção visual a 1280×720 passou, com screenshots. Um segundo
render usou disponibilidade facial simulada somente no helper temporário para
verificar a linha de instrução longa; a instrumentação confirmou que o helper
identifica o PID/início do próprio Hyprlock. Não se simulou sucesso PAM, não se
alterou PAM para o teste e não se introduziu qualquer password.

[Pré-visualização nativa, com disponibilidade facial simulada](../audit/2026-09-13-face-auth-ui/lock-preview.png).
O layout English (US) mostrado pertence ao compositor de teste; a instalação
mostra o layout real por `$LAYOUT`.

O primeiro ensaio sem runtime definido abortou antes de arrancar. O backend
exclusivamente headless não arrancou; o teste final usou um compositor aninhado
com saída headless privada. Foram corrigidos apenas caminhos/permissões do
ensaio e seleção de socket novo após um socket antigo ter sido encontrado.
Os processos de teste terminaram e os diretórios temporários foram removidos.
A sessão original ficou com o mesmo Hyprland/Quickshell, sem bloqueio ou reinício.
Os crash reports de ensaios falhados foram preservados, não limpos globalmente.

16 ficheiros instalados conferem em hash/proprietário/modo. Os 55 assets de source
e 53 instalados conferem com os respetivos manifestos. Patch final aplicado ao
commit upstream fixado produz exatamente o `compare.py` instalado. Sintaxe Python,
PKGBUILD e whitespace passam; Host sem unidades falhadas.

O Hub estava parado. Captura real, reconhecimento da cara, timeout físico,
password e aceitação visual no monitor do utilizador continuam por confirmar.
Nenhum modelo biométrico nem imagem de câmara foi copiado para os testes.

## Recuperação e manutenção

Backup: `/var/lib/apx/backups/20260913T223101Z-face-ui-status/`.
O manifesto contém os 16 predecessores, destinos, metadados e hashes. Contém
igualmente o driver de preview, screenshot, log do Hyprlock e prova de parentesco.
Restaurar os destinos em lugar com os metadados registados; restaurar seed e
manifestos juntos. As mudanças entram na próxima abertura do bloqueio.

O `compare.py` do Hub foi atualizado em lugar, sem transação de pacotes. A receita
`howdy-apx` avança para pkgrel 4 e fixa o hash do patch novo. A base de dados do
pacman conserva a versão anterior; uma reinstalação do pacote antigo substituiria
a atualização do marcador. Usar a receita revista numa futura reconstrução.
O adaptador datado recusa um predecessor diferente. Isto é correção limitada do
piloto experimental, não uma nova arquitetura de autenticação partilhada.

Referências: [widgets e variáveis do Hyprlock](https://wiki.hypr.land/Hypr-Ecosystem/hyprlock/)
e [Howdy no commit fixado](https://github.com/boltgolt/howdy/tree/d3ab99382f88f043d15f15c1450ab69433892a1c).
Sem commit, push, instalação de reconhecimento nos workloads ou reinício da sessão.
