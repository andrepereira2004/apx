# Verificação de eliminação — 2026-10-04

**Não é possível confirmar eliminação completa: existem cópias recuperáveis.**
Esta verificação não apagou ficheiros, snapshots nem partições.

## Confirmado em leitura

- Os três restos de criações nunca publicadas `developer`, `trabalharei` e
  `workkk-from-jome` já não têm diretórios ativos em `/var/lib/apx/environments`.
  O journal regista a recuperação aprovada em 2026-10-04 às 11:16:36 UTC.
- Permanecem **seis snapshots de home**, dois por nome, sob
  `/.snapshots/local-recovery/environment-NOME-home/`, com datas
  `20260927T161241Z` e `20260929T142237Z`. São subvolumes Btrfs reais
  (IDs 417/427, 423/433 e 424/434), não meras referências no journal.
- Existe `audit/2026-09-21-input-monitors/windows-lab/disk.raw` neste checkout:
  disco esparso de 476,94 GiB lógicos, aproximadamente **31 GiB alocados**.
  O código de preparação confirma que é o laboratório Windows de setembro:
  partições Windows criadas de novo e media de instalação copiada do piloto.
  Não é simplesmente um log nem uma cópia integral dos dados do Windows pessoal.
- Esse disco também existe dentro dos **dois snapshots `system`** de
  `/.snapshots/local-recovery/`, no mesmo caminho relativo sob `root/`.
  Não somar os tamanhos como espaço recuperável: Btrfs partilha extensões.
- Os dez payloads `.wim`/`.efi` explicitamente removidos no inventário
  `/var/lib/apx/cleanup-20260927.md` continuam ausentes nos caminhos registados.
- Os Windows `windows` (Pessoal, p3) e `windows-testes` (Faculdade, p5)
  continuam registados e `ready`. Foram preservados. `ntfsls` leu a raiz de
  ambos, sem montar em escrita: não existe `Windows.old` nessas raízes.
  Existem `$Recycle.Bin`, `Recovery` e `System Volume Information`; a ausência
  de `Windows.old` não prova a ausência de todo o histórico recuperável.
- Permanecem imagens de instalação/recuperação Windows na migração nativa
  e ISO comum. Estes ficheiros não foram confundidos com environments apagados.
- Os rollbacks de atualização e snapshots de outubro correspondem aos cinco
  environments Linux atualmente registados. Não são sobras automaticamente
  descartáveis de environments eliminados.

## Cobertura e limites

O script repetível `scripts/portable/audit-deleted-environments.py` cruza nomes
eliminados no journal com registos ativos, inventaria backups e imagens, e lista
subvolumes Btrfs. O inventário bruto ficou em
`tmp/deletion-audit-20261004.json` (não versionado, para evitar copiar nomes de
ficheiros pessoais). A busca por nomes inclui falsos positivos de diretórios
como `test` e `work`; não é uma lista autorizada de remoção.

Foram inspecionados `/var/lib/apx`, `/.snapshots/local-recovery`, backups de
código em `/root/apx-audit-backups`, o laboratório neste checkout e as raízes dos
dois NTFS. A pesquisa adicional na pen montada não identificou imagens de
backup pelas extensões procuradas. Discos desligados, backups externos/cloud,
conteúdo de todos os arquivos comprimidos, ficheiros renomeados e blocos livres
não estão cobertos. Não há prova de apagamento seguro/irrecuperabilidade.

A pergunta ao owner distingue verificar de eliminar cópias. Sem resposta, não
se apagam snapshots do sistema inteiro nem os dois Windows válidos.
