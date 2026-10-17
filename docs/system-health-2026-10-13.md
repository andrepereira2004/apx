# Saúde do sistema e limpeza — 2026-10-13

O proprietário autorizou explicitamente recontar quotas, limpeza necessária e
diagnóstico geral. Piloto Lenovo 82JU, hostname apx-host, identidade fixa
confirmada. Faculdade manteve a mesma geração. Não houve commit/push, atualização
geral de pacotes, alteração de drivers, partições, encriptação ou bootloader.

## Resolvido e verificado

| Trabalho | Resultado |
|---|---|
| Recontagem das quotas existentes | Inconsistent=no, limites ativos e sem override |
| Contabilização APX | Cache dos cinco Environments voltou a ser atualizado pelo serviço existente |
| Scrub Btrfs apenas de leitura | Concluído em 74 s; aproximadamente 185 GiB; nenhum erro encontrado |
| Espera pela rede | Serviço passou a sucesso; espera por qualquer uplink físico routable, Ethernet ou Wi-Fi |
| Pacotes | Base de dados e existência de ficheiros verificadas no Host e nos cinco Environments, sem erros |
| Limpeza | 24 versões antigas de distribuições Codex removidas; atuais, anteriores e versões mapeadas em processos preservadas |
| LocalSend | Instalado apenas na Faculdade, com três pequenas dependências Ayatana assinadas pelos mantenedores Arch |

A limpeza retirou 8,83 GiB de ficheiros das versões antigas no sistema ativo.
Os snapshots preservados ainda referenciam esses dados, pelo que **não se afirma
uma recuperação física de 8,83 GiB**. O filesystem continua com cerca de 30 GiB
livres. Não foram eliminados snapshots, imagens Windows, documentos, históricos,
credenciais ou Environments. Mantidos os dois releases mais recentes de cada
distribuição Codex e todos os usados por processos na verificação.

A verificação de ficheiros pacman confere existência; não é uma auditoria de
segurança nem uma comparação criptográfica de todos os conteúdos modificados.
Não houve ensaio de reinício, round trip APX ou monitores externos nesta fase.

## Alterações e reversão

- Novo /etc/systemd/network/20-wired.network.d/50-apx-optional-online.conf:
  RequiredForOnline=no para Ethernet; configuração original preservada.
- Novo /etc/systemd/system/systemd-networkd-wait-online.service.d/50-apx-uplinks.conf:
  --interface=eno1:routable --interface=wlan0:routable --any --timeout=30.
  Teste direto passou, seguido de execução do serviço com Result=success.
  networkctl reload não reiniciou Wi-Fi. O primeiro teste só com Ethernet
  opcional continuou a esperar por links initialized, justificando o filtro
  explícito dos uplinks. Reversão: retirar apenas os dois drop-ins, executar
  networkctl reload e systemctl daemon-reload. Backup e registo em
  /var/lib/apx/backups/20261013-system-health.
- LocalSend 1.18.2-4 é um empacotamento APX do binário oficial 1.18.2, não uma
  release upstream 1.18.2-4. SHA256 upstream confirmado; manifesto do pacote em
  /var/lib/apx/package-artifacts/localsend-bin-v1.json. Dependências novas:
  libayatana-appindicator 0.6.0-2, libayatana-indicator 0.9.5-1 e ayatana-ido
  0.10.4-1. Nenhuma biblioteca base atualizada. Cópias/pacotes intermédios tiveram
  problemas de permissões e dependências, corrigidos no pacote final; última
  transação sem avisos. Bibliotecas do executável e ficheiros dos quatro pacotes
  passaram. Backup, inventário anterior e instruções de remoção em
  /var/lib/apx/backups/20261013-localsend.
- Máscara de suspensão apenas em /run e inibidor temporário removidos ao fim.
  A suspensão original voltou a estar disponível. A primeira tentativa de scrub
  e a segunda foram interrompidas por suspensão; um pedido já em curso passou
  apesar do inibidor. A terceira, protegida pela máscara temporária, concluiu.
  Não ocultar os dois ensaios interrompidos como verificações completas.

## Problemas a acompanhar

| Prioridade | Evidência e próximo trabalho |
|---|---|
| Alta | Aproximadamente 137 GiB de blocos atribuídos ao diretório da migração Windows. Original e prepared são imagens de recuperação; não apagar sem determinar referências, estado da migração e provas de arranque/rollback. Tamanhos lógicos não equivalem a espaço físico libertável. |
| Alta | Filesystem abaixo da reserva de 30 GiB usada pelo script de snapshots semanais; a política pode saltar snapshots novos. Rever retenção por função e referências, preservando recuperação útil. |
| Média | Quotas completas podem voltar a ficar inconsistentes em operações de snapshots. Investigar lifecycle e política de contabilização; não desativar limites nem migrar para squotas automaticamente. |
| Média | Câmara USB 1-3 tem erros de protocolo -71 e falhas UVC. Investigar dispositivo, energia/suspensão e firmware de forma separada, sem desligar os mecanismos de autenticação existentes. |
| Média | logind repete erro de alias autovt@tty1 quando getty@tty1 está mascarado pela APX. Rever em conjunto com o retorno e recuperação de consola; não ativar getty durante a sessão gráfica. |
| Média | LocalSend apresenta avisos/exceção de conectividade porque o plugin assume NetworkManager. Abriu como janela Wayland nativa, mas a rede/transferência não estão aceites. Preferir corrigir a deteção para networkd em vez de instalar outro gestor de rede. |
| Baixa | Mensagens ACPI de símbolo BIOS ausente; sem correlação demonstrada com uma falha funcional nesta auditoria. Firmware já tem fwupd; avaliar atualizações sem as aplicar automaticamente. |

SSD: SMART passou, 3% de desgaste estimado, zero erros de media/integridade;
207 desligamentos não seguros acumulados. As 13 662 entradas de erro incluem
Invalid Field in Command; a contagem não demonstra falha física do SSD.
Btrfs mantém contador acumulado de corrupção 79, sem incremento observado.
NVIDIA RTX 3060 a 40 °C no momento consultado, sem Xid ou reset amdgpu encontrado
no intervalo consultado. Estas leituras não substituem testes de carga ou de
suspensão/monitores externos.

## iPhone e opções futuras

Nenhuma exceção de rede foi aberta. LocalSend abriu em Wayland nativo; o endpoint
local não passou o ensaio HTTP/TLS e a aplicação já não estava em execução na
verificação final, sem causa de saída estabelecida. Não se afirma transferência
funcional. Falta IPv4 do iPhone e app LocalSend no dispositivo para configurar e
testar comunicação limitada, incluindo encerramento ao sair da Faculdade.
Toggle para novos Environments permanece uma proposta, não implementada.

Evidência: audit/2026-10-13-system-health/summary.json e ficheiros companheiros.
Referência para os custos e limites de qgroups:
https://btrfs.readthedocs.io/en/latest/btrfs-quota.html
