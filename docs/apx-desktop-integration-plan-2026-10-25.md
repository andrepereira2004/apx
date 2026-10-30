# Plano de integração e acabamento APX — 2026-10-25

Estado: proposta para discussão, autorizada apenas a elaboração do plano nesta etapa.
Não representa funcionalidades implementadas, novos pacotes aprovados ou aceitação visual.

## Objetivo

Dar às aplicações APX, GTK, Qt, Electron, Flatpak e outras uma experiência
coerente, responsiva e cuidada. macOS é uma referência de continuidade e
previsibilidade; APX mantém a sua identidade e o isolamento dos Environments.
A tecnologia e o formato de instalação são eixos distintos: Flatpak pode conter
uma aplicação GTK, Qt ou Electron. A compatibilidade precisa de ser verificada
por aplicação, versão e Environment, sem prometer uniformidade universal.

## Base já encontrada e limites da observação

Inspeção do repositório, não uma auditoria do desktop em execução:

- `config/environment-shell-v1/xdg-desktop-portal/portals.conf` seleciona
  Hyprland/GTK e GTK para escolher aplicações e ficheiros.
- `local/bin/apx-desktop-activation-v1` publica o contexto de sessão, pede
  portais GTK/Qt e configura fontes/ícones; inicializa associações de browser
  em falta. A associação de diretórios a Thunar é intencional e deve manter-se,
  conforme decisão explícita do proprietário em 2026-10-25.
- GTK3/GTK4 têm Selawik 11, APX-Graphite e Adwaita-dark configurados.
- Existem CSS GTK, adaptação específica do seletor e regras de janela para
  diálogos; o seletor tem geometria de 78% por 82% do monitor na configuração.
- Aparência global/local, notificações Mako e controlos MPRIS já têm trabalho
  documentado. Confirmar cobertura efetiva antes de criar substitutos.
- O histórico de hoje regista curvas coordenadas e continuidade de pastas.
  Amostras frameSwapped não demonstraram redução dos bloqueios nem mediram
  apresentação GPU ou tempo de arranque das aplicações.
- Decisão atual do proprietário: Rofi com animação de entrada/saída; sem
  transições internas, prefetch de pastas ou reinstalação das experiências rejeitadas.

## Seleção inicial de integrações

| Área | Proposta | Prioridade | Condição de adoção |
| --- | --- | --- | --- |
| Abrir/guardar e escolher aplicações | Consolidar portais existentes | Alta | Filtros, cancelamento, permissões e foco corretos em cada app |
| Foco e diálogos | Corrigir associação à janela, geometria e retorno do foco | Alta | Sem roubar foco nem esconder diálogos noutra área de trabalho |
| Abrir ligações e ficheiros | Associações locais previsíveis, respeitando escolhas | Alta | Abrir no Environment de origem e evitar janelas duplicadas |
| Fontes, ícones, superfícies | Consolidar padrões já aceites | Alta | Legibilidade, escala e preferências locais preservadas |
| Notificações | Rever identidade, ações e destino ao clicar | Média | Validar entrega e navegação sem mensagens reais |
| Multimédia | Completar cobertura do controlo local existente | Média | Só leitores compatíveis, sem controlo sobre outro Environment |
| Copiar/colar e arrastar ficheiros | Verificar texto, imagens e ficheiros entre apps locais | Média | Não ampliar partilha entre Environments |
| Partilha de ecrã | Validar seleção e término de captura via portais | Média | Conteúdo e permissões limitados à sessão autorizada |
| Pesquisa unificada | Explorar apps, ficheiros e ações locais | Posterior | Resposta rápida, âmbito explícito, sem indexação global por defeito |
| Pré-visualização por tecla | Pequeno protótipo opcional | Posterior | Cobertura útil, abertura rápida e cancelamento imediato |
| Menu global estilo macOS | Investigar apenas se houver benefício comprovado | Adiar | Cobertura desigual exige avaliação antes de qualquer adoção |
| Temas invasivos e adaptações internas por app | Evitar como estratégia geral | Adiar | Exceção só com ganho claro, recuperação e custo de manutenção conhecido |

## Fase 1 — Inventário e referência de qualidade

Entregável: matriz por aplicação/Environment com versão, toolkit, instalação,
Wayland/XWayland, abrir/guardar, ligações, foco, notificações, multimédia e escala.
Estados: confirmado, falha reproduzida, não suportado, não testado.
Começar por Ficheiros/Thunar, Brave, Thunderbird e ZapZap, confirmando primeiro
onde estão instalados. Incluir uma aplicação Flatpak e uma Electron se existirem;
não instalar só para preencher a matriz. Hub conserva o seu papel mínimo.

Percursos com ficheiros descartáveis: selecionar um anexo sem enviar mensagem;
guardar/reencontrar um ficheiro; abrir ligação local controlada; cancelar um
seletor; alternar entre aplicação e diálogo; reabrir aplicação já em execução.
Registar comportamentos, tempos e imagens apenas de conteúdo de teste.
Nenhuma notificação a contactos, envio de email ou alteração de conta.

## Fase 2 — Primeira experiência pequena

Escolher o percurso com maior fricção demonstrada. Candidato inicial:
abrir/guardar no Brave e anexar no Thunderbird, verificando o seletor existente,
parentesco do diálogo, tamanho, foco, teclado e preservação de filtros.
A escolha final depende da matriz: se o percurso já estiver bom, avançar para
a falha real seguinte em vez de o reescrever.

Preparar alterações no repositório, usar primeiro um Environment de teste
claramente descartável e só depois propor adoção nos ambientes de uso.
Cada experiência deve ter hipótese, ficheiros afetados, evidência antes/depois,
limitações e recuperação. Preferir interfaces públicas e configurações existentes;
não criar um novo serviço ou backend de portal sem necessidade demonstrada.

## Fase 3 — Consistência visual e de interação

Documentar valores atuais de fonte, cor, ícones, contorno, raio, espaçamento,
foco e movimento. Consolidar os valores aceites, sem redesenho geral implícito.
Comparar GTK3, GTK4/libadwaita, Qt e conteúdo web separadamente; quando uma app
não seguir o tema, procurar primeiro opções suportadas pela própria app.
Verificar contraste, texto ampliado, escala fracionária, teclado e movimento
reduzido. Preservar atalhos próprios das apps; harmonizar ações APX comuns.
Não forçar títulos, sombras ou decoração em duplicado.

## Fase 4 — Serviços e distribuição

Tratar notificações, multimédia, captura e transferência local de dados em
experiências independentes. Separar identidade da aplicação e identidade do
Environment; ações devem permanecer no contexto autorizado.
Distribuir padrões revistos pelo seed independente e versionado, nunca copiando
o Hub vivo. Preservar personalizações locais e testar um Environment novo,
um existente e um com preferências alteradas. Não partilhar bases de dados,
credenciais, histórico ou sockets de sessão entre Environments por conveniência.

## Critérios de aceitação

- Abrir, guardar e cancelar funcionam; filtros e nomes não se perdem.
- O diálogo aparece no contexto certo e devolve o foco corretamente.
- Thunar mantém-se como gestor de ficheiros predefinido; restantes preferências
  respeitam as decisões explícitas do proprietário.
- Percursos locais funcionam com teclado e na escala de utilização real.
- Separar tempo até aparecer a janela de tempo até a app aceitar interação.
  Comparar arranques frios e quentes separadamente, em várias repetições e nas
  mesmas condições; reportar mediana e variação, sem prometer metas sem baseline.
- Medir pausas nas transições e custo em repouso; não aceitar melhoria visual
  que introduza atividade contínua desnecessária ou bloqueie a interação.
- Só declarar melhoria de fluidez com evidência adequada e observação do
  proprietário; callbacks do shell não provam fluidez interna de outra app.
- Nenhum alargamento implícito de acesso entre Environments; recuperação testável.

## Próximas decisões

1. Confirmar as aplicações prioritárias a partir do inventário e do uso diário.
2. Selecionar o primeiro percurso demonstravelmente problemático.
3. Rever uma proposta concreta de integração e respetivo antes/depois.
4. Adotar, ajustar ou rejeitar cada experiência separadamente.

Preferência inicial proposta: abrir/guardar + foco, depois coerência visual,
depois notificações e multimédia. Pesquisa e pré-visualização ficam opcionais.

## Referências

- https://docs.flatpak.org/en/latest/portals.html — suporte de portais em GTK/Qt;
  depende das APIs utilizadas pela aplicação.
- https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.FileChooser.html
  — contrato de abrir/guardar e identificação da janela que pede o diálogo.
- `CURRENT_HANDOFF.md` — estado mais recente, incluindo decisões sobre Rofi.
- `docs/appearance-preferences-2026-10-16.md` — aparência e serviços já trabalhados.

## Registo desta etapa

Criado apenas este plano e uma entrada no handoff. Não foram alterados runtime,
pacotes, serviços ou configurações do desktop; sem commit ou push.
