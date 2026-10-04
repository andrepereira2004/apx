# Touchpad e fontes próximas do Windows — experiência de 2026-09-13

Pedido: movimento de touchpad mais suave, próximo do macOS, e fonte mais parecida
com Windows no sistema, preservando os botões da Quickshell. Foi pedida clarificação
opcional sobre a exceção; sem resposta, avançou-se com a interpretação anunciada:
botões da barra superior preservados, menus (incluindo os seus controlos) com a
nova fonte. A alteração é reversível e aguarda avaliação física/visual.

## Instalação

Nas cinco homes existentes e no seed independente de futuros environments:

- Selawik 1.01 nos defaults GTK3/4, sans-serif/system-ui, Rofi, Hyprlock e menus
  da Quickshell. Os cinco pesos são fontes locais de cada Environment, com licença.
  FontLoader regista-os também no processo Qt já em execução.
- Cascadia Mono 2407.24 em monospace, preferências de texto monoespaçado e Kitty.
  Incluídos regular, bold, italic e bold-italic, com licença; cada ficheiro cabe
  no limite existente de 1 MiB do seed. Nenhum limite de admissão foi aumentado.
- Os cinco `BarButton.qml` permanecem exatamente iguais, com Adwaita Mono.
- Os defaults de arranque aplicam Selawik 11/Cascadia Mono 11 via GSettings;
  os dois valores foram também aplicados à sessão Hytale ativa. O cache de fontes
  foi atualizado nessa sessão. Aplicações com fontes próprias ou fontes guardadas
  em memória podem exigir reabertura/configuração própria. Não se reescreveram
  estilos de páginas web nem fontes internas dos jogos.
- O Kitty do Hub conserva a sua paleta, transparência, tamanho e restantes opções;
  só a família foi alterada. O primeiro ensaio do adaptador recusou corretamente
  substituir essa configuração diferente do seed, antes de qualquer escrita.

Fontes oficiais: [Microsoft Selawik](https://github.com/microsoft/Selawik), uma
alternativa aberta à Segoe UI, e [Microsoft Cascadia Code/Mono](https://github.com/microsoft/cascadia-code/releases/tag/v2407.24).
Selawik_Release.zip 1.01 SHA-256:
`3f62c51e05e3b5a1e6241cf92a371f0be2ea1183aa87b30718bbd40832a8d423`.
As licenças e fontes selecionadas estão no seed; o arquivo temporário Cascadia
foi eliminado automaticamente depois da extração. Não se instalaram pacotes
nem fontes no Host ou na base imutável.

## Perfil de touchpad

Bloco específico para `elan06fa:00-04f3:31dd-touchpad` nas cinco configurações Lua
e no seed Lua. Preserva outras personalizações e não altera o rato externo:

| Opção | Antes | Experiência |
| --- | --- | --- |
| accel_profile | não explicitado, default do libinput | adaptive |
| sensitivity | 0 global | -0.15 apenas no touchpad |
| scroll_factor | default 1 | 0.65 apenas no touchpad |
| natural_scroll | true | true |

O objetivo é controlar melhor movimentos pequenos mantendo aceleração para
percorrer distâncias maiores, e tornar a deslocação de páginas menos brusca.
Não foi adicionada interpolação artificial do cursor, nem se reproduziu a curva
proprietária ou a inércia do macOS. A sensação depende do hardware, do libinput
e das aplicações. Só o utilizador pode confirmar se esta primeira afinação é
mais confortável; não se recolheram eventos físicos nem se alegou essa confirmação.
A configuração é específica do dispositivo observado, não uma regra universal
para outros portáteis.

Referência: [input e dispositivos do Hyprland](https://wiki.hypr.land/Configuring/Basics/Variables/).

## Verificação

35 testes relevantes passam: defaults 14, seed desktop 7, menus 8 e base 6.
Foi atualizada a expectativa antiga de fonte do corpo da Quickshell. A comparação
separada dos cinco componentes de barra confirma que continuam em Adwaita Mono.
123 ficheiros e metadados instalados conferem; source 66 e seed instalado 64 assets
conferem com os seus manifestos, preservando as diferenças anteriores entre eles.
Python do adaptador e whitespace passam.

Na sessão ativa, fc-match confirma Selawik para sans-serif e Cascadia Mono para
monospace. Quickshell recarregou com `Configuration Loaded`. A Central de Controlo
abriu e terminou a animação, foi capturada e inspecionada com a nova tipografia,
e ficou fechada. Não foram acionados controlos de hardware nesse teste.
Screenshot: `audit/2026-09-13-touchpad-font-trial/controls.png`.

Hyprland não reporta erros e o inventário de dispositivos confirma scrollFactor
0.65 no ELAN, com os restantes dispositivos preservados. `defaultSpeed` nesse
inventário é o default do dispositivo, não prova da sensibilidade corrente.
Tentativas de consulta per-device por `getoption` devolveram `no such option`;
não se apresenta essa consulta como confirmação independente do valor -0.15.
A configuração específica foi aceite pelo compositor, mas a sensação do cursor
permanece por validar fisicamente. APX saudável, sem unidades Host falhadas.
Não se reiniciou a sessão nem se fecharam aplicações do utilizador.

## Recuperação

Backup: `/var/lib/apx/backups/20260913T224506Z-touchpad-font-trial/`.
O manifesto regista destinos, originais, ficheiros novos, metadados e hashes.
Restaurar os originais em lugar e remover apenas fontes novas nele identificadas,
restaurando seed/manifestos juntos. Os dois valores GSettings da sessão podem
ser repostos através do helper de ativação restaurado; antes desta experiência
os defaults eram Adwaita Mono 11 para interface e monospace. Atualizar cache de
fontes/reabrir aplicações que o necessitem. É possível reverter apenas o bloco
do touchpad, ou apenas as fontes, preservando os restantes trabalhos.
Sem commit ou push.

## Correção após experiência do utilizador — 2026-09-13, 23:57

O utilizador pediu Selawik também nos botões da Quickshell e rejeitou a sensação
do touchpad como demasiado sensível/escorregadia no browser. Esta observação
substitui a aceitação ainda pendente do primeiro perfil.

Selawik está agora nos cinco BarButton.qml e no seed. O perfil ELAN passa de
adaptive/-0.15/0.65 para **flat/-0.30/0.35** (aceleração/sensibilidade/scroll).
O perfil flat aplica um fator constante, sem aumento dependente da velocidade,
conforme a [documentação libinput](https://wayland.freedesktop.org/libinput/doc/latest/pointer-acceleration.html).
O scroll enviado para as aplicações fica aproximadamente 46% menor que no ensaio
anterior para o mesmo gesto. Preserva a direção natural, outros dispositivos,
gestos, configuração do browser e toda a configuração fora desse bloco.
A inércia própria do browser não foi desativada; não se promete que a configuração
elimine toda a sensação de deslizamento. A nova sensação requer experiência física.

Instalado sem reinício em cinco homes e defaults futuros. Quickshell recarregou,
a barra foi capturada/inspecionada com Selawik, Hyprland não reporta erros e o
inventário efetivo confirma scrollFactor 0.35 apenas no touchpad. Na observação
final o browser não estava aberto; não se apresenta isto como teste de scroll
físico no Brave. 29 testes relevantes passam, com 15 ficheiros/metadados e ambos
os manifestos completos verificados. Sem unidades Host falhadas.

Backup desta correção: `/var/lib/apx/backups/20260913T225741Z-touchpad-refine/`.
Inclui os 15 predecessores/metadados/hashes e `bar.png`. Restaurar apenas o bloco
do touchpad ou os componentes/manifestos correspondentes para reversão seletiva.
O adaptador `deploy-touchpad-refine-20260913.py` é específico deste predecessor.
Sem commit/push, reinício do compositor ou encerramento de aplicações.

## App scroll and bar glyph alignment (2026-09-14)

Owner likes pointer motion but reports Brave scrolling too fast and terminal too
slow. Installed touchpad-only window overrides: Brave 0.25 (previously device
0.35), Kitty and the existing Host console 0.55. Device defaults remain flat,
-0.30, scroll 0.35. Rules replace, rather than multiply, the device factor.
Active terminal property reads 0.55; Brave was closed, so physical browser feel
is pending. The requested horizontal distinction is still unconfirmed; these
native scalar overrides affect both axes and do not implement independent axes.

Selawik remains throughout QuickShell. Bar labels have demi-bold weight, 0.3px
tracking and rounded content widths with 12px side padding. Control Centre keeps
the owner-required literal [|] / [A] transition: equal glyph cells and visible-ink
vertical centring remove compression and font baseline asymmetry. A proposed
sliders icon was rejected and removed. Both final states were inspected in live
screenshots; popup closed after verification. All five homes and independent
future seeds are synchronized without restarting the session.

29 focused tests pass; the shortcut test now permits the exact existing terminal
class in a scroll rule, while retaining its forbidden launch checks. Lua has no
configuration errors. Source/installed seed hashes and metadata were checked.
Initial before-change backup: `/var/lib/apx/backups/20260913T230721Z-app-scroll-bar`.
Final deployment backup and screenshots:
`/var/lib/apx/backups/20260913T230906Z-app-scroll-bar`.
For rollback, restore only manifest-listed files with original metadata, restore
the corresponding source assets, and keep runtime/seed digests synchronized.
No commit or push.

Native rule reference: https://wiki.hypr.land/Configuring/Basics/Window-Rules/

Owner follow-up: every bar label/symbol now shares 14px Selawik DemiBold and
visible-ink vertical centring, including normal/alternate states; literal [|]/[A]
remain. Final consistency backup: `/var/lib/apx/backups/20260913T231013Z-app-scroll-bar`.
15 relevant tests and installed hash/metadata checks pass; live bar inspected.
