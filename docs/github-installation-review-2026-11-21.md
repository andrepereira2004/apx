# GitHub e instalação num PC novo — 2026-11-21

## Conclusão

O branch `agent/defer-local-model-phase10` era o mais avançado: 112 commits à
frente do antigo `master`, mais as alterações locais de 20–21 de novembro.
Foram comparados os seis branches remotos. `agent/physical-headless-handoff`
e `apx-arch-base-v1` já eram antepassados do branch atual. Os branches
`physical-bootstrap-dns-recovery-v1` e `physical-headless-quota-v4-fix` tinham
uma correção exclusiva cada; ambas foram integradas com preservação do histórico.
O resultado consolidado destina-se ao `master`, sem reescrever ou eliminar
branches remotos.

**O instalador ainda não reproduz todas as funcionalidades do piloto físico.**
Ter os ficheiros atuais no GitHub e incluí-los no pacote não equivale a ativar,
configurar e validar os respetivos serviços num computador novo.

## Correções desta revisão

- `install.sh` usava por predefinição o antigo branch `apx-arch-base-v1` e o
  instalador sem interface. Agora obtém `master` e chama `install-apx-full.sh`.
  Continua a exigir um Arch novo, arranque normal, root, Btrfs e espaço livre;
  mantém `--check` por predefinição e recusa uma instalação APX existente.
- O README usa `master` na clonagem e explicita os limites de cobertura.
- Integração das correções antigas de DNS/recuperação de Development incompleto
  e consulta de qgroups sem o filtro que ocultava os subvolumes.
- Um teste textual de duplo clique foi atualizado para reconhecer a proteção
  atual durante a reordenação e a recusa de abrir destinos indisponíveis.

## Cobertura e lacunas observadas

O manifesto gráfico verifica 765 ficheiros de fontes. Os 335 assets do shell
correspondem aos hashes declarados no repositório. O empacotamento inclui os
novos módulos Python de versões de aplicações e recuperação de espaço Windows.

Contudo, `apx-portable-full-runtime.py::configure_features` substitui o caminho
de instalação de aplicações do piloto: instala os pacotes declarados, mas não
executa o mesmo provisionamento de artefactos de terceiros. Por isso, incluir
`apx_package_freshness.py` não garante essas aplicações numa instalação portátil.
Os serviços portáteis também não constituem uma instalação completa dos brokers
de partilha ou do ciclo Windows nativo/recuperação de espaço. Esses adaptadores
físicos exigem generalização e admissão próprias, sem copiar identidades de disco.

A comparação só de leitura encontrou 165 módulos instalados idênticos às fontes
e 14 diferentes. Onze assets da seed instalada diferem do repositório, incluindo
wallpapers, configuração Hyprland, helpers de aparência/update e QML. Estes
resultados são candidatos a revisão: diferenças podem ser adaptações do piloto
ou personalização e não autorizam substituir automaticamente as fontes.
O relatório detalhado é `audit/2026-11-21-github-installation/readiness-final.json`.
A primeira medição, `readiness.json`, antecede a inclusão no índice Git dos novos
módulos; as três ausências de nomes nessa medição estão resolvidas na final.

Dados pessoais, credenciais, Environments existentes e aplicações já instaladas
exigem migração/backup separado. O instalador de raiz não atualiza este PC.
O instalador de disco vazio continua a recusar discos com dados, não configura
encriptação e não instala Windows.

## Validação

- 256 testes focados passaram, incluindo instalação portátil/gráfica/disco,
  Windows nativo, transições, aplicações atuais, partilha, energia, bootstrap
  e quotas. Registo: `audit/2026-11-21-github-installation/tests.txt`.
- Verificação dos 765 ficheiros e hashes das seeds passou.
- Sintaxe Bash dos pontos de entrada e bootstrap passou.
- A release nativa instalada mantém `enabled=true`, sem erros de validação.
- Não foi executada instalação, formatação, reinício ou atualização do Host.

A evidência VM de outubro é histórica: o manifesto dessas fontes já não
corresponde integralmente às fontes atuais. Não foi repetida uma instalação
limpa nesta revisão. O plano existente requer 128 GiB livres para preservar
96 GiB de reserva e usar 32 GiB de trabalho; faltam aproximadamente 3,1 GiB.
Também não existe o QEMU provisionado no Environment descartável previsto.

Para comprovar equivalência completa faltam rever as diferenças instaladas,
generalizar os serviços/aplicações em falta e repetir instalação limpa, segundo
arranque, isolamento, recovery e interação gráfica, seguidos de testes em
hardware real para GPU, Wi-Fi, áudio e suspensão.
