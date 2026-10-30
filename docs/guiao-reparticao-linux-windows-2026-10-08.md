# Guião para voltar a repartir espaço entre Linux/APX e Windows

Data: 08-10-2026. Referência: operação concluída em 07-10-2026 neste computador.

## O que é repetível

É possível repetir a abordagem: preparar e verificar uma imagem Windows maior,
arrancar numa manutenção independente, reduzir o Linux, deslocar o Windows,
verificar a nova disposição e atualizar os registos APX. Não é uma operação
online: o Linux normal e os ambientes ficam parados durante a manutenção.

Os scripts guardados são específicos da operação antiga e NÃO devem ser
executados novamente sem adaptação. Contêm tamanhos, posições, hashes e
identidades da situação anterior. Este documento é um guião para o responsável
pela próxima intervenção, não um botão automático de repartição.

## Backup: o que se pode reaproveitar

O backup existente é útil para recuperar o estado de 07-10-2026. Não inclui
ficheiros, aplicações ou alterações posteriores. Restaurá-lo no futuro recua
TODO o SSD interno para esse estado, incluindo os outros Windows e o Linux.

Nesta operação, a imagem completa e verificada do SSD antes da primeira escrita
foi uma condição do processo. Para repetir a mesma proteção, é necessária uma
imagem atual e verificada antes da próxima alteração. O facto de ter resultado
uma vez não elimina falhas de energia, disco ou cálculo. Um snapshot Btrfs no
mesmo SSD não substitui uma cópia externa numa alteração de partições.

Não é necessário criar cópias repetidas enquanto nada está a ser repartido.
Numa futura intervenção, verificar primeiro o que já existe: uma imagem da
MESMA situação atual pode ser reaproveitada após verificar o hash da imagem e
do disco de origem, como o executor antigo já fazia. Uma imagem antiga, mesmo
intacta, não serve como backup atual. Não apagar o backup anterior para abrir
espaço antes de existir uma alternativa verificada. O SSD externo já preparado
pode ser usado sem o voltar a formatar, se tiver capacidade disponível.

## Estado de referência após a operação

- SSD interno: Samsung, série S4DYNX0R253702, 512110190592 bytes.
- Linux: /dev/nvme0n1p2, LUKS + Btrfs, cerca de 216,4 GiB de partição.
- Windows Pessoal: /dev/nvme0n1p3, 170 GiB.
- Windows Faculdade: /dev/nvme0n1p5, 80 GiB.
- Restantes partições EFI/MSR/instalador preservadas.
- SSD externo: Samsung 870 QVO, série S5SVNF0R241427A.
- Backup ext4: UUID 7cac2282-db7f-4945-9d58-053c1c46deea.

Estes valores são históricos: medir novamente antes de qualquer ação.
GiB são as unidades utilizadas nos tamanhos APX; 512 GB comerciais são cerca
de 476,9 GiB. Espaço livre no Linux não implica espaço livre reparticionável:
a redução precisa de margem para os dados e para o funcionamento do APX.

## Passos para a próxima intervenção

1. Confirmar com o proprietário qual Windows deve crescer e quanto espaço
   pode sair do Linux. Esta nota não autoriza futuras escritas em discos.
2. Identificar os discos por série e UUID, não apenas por /dev/sda. Registar GPT,
   setores, GUIDs, EFI, LUKS, Btrfs, NTFS e registos APX atuais. Confirmar espaço
   usado e margem de redução, saúde do disco e acesso à recuperação LUKS.
3. Fazer encerramento completo do Windows e verificar o NTFS; tratar primeiro
   hibernação ou inconsistências. Verificar o Btrfs com scrub só de leitura e
   guardar os contadores de erros. Não limpar sinais de erro para prosseguir.
4. Criar um novo diretório de operação, sem substituir a evidência anterior.
   Calcular uma nova GPT, alinhamento e tamanho Btrfs descontando o cabeçalho
   LUKS. Preservar GUIDs e todas as partições alheias à transferência.
5. Copiar e verificar o Windows atual. Preparar no SSD externo a imagem NTFS
   maior; ajustar o campo de início NTFS à nova posição e verificar a imagem.
   Comparar hashes e simular o fluxo em disco de laboratório antes do hardware.
6. Preparar imagens de manutenção e recuperação independentes, assinadas para
   Secure Boot. Verificar assinaturas, plano embutido, identidades, acesso ao
   SSD externo e arranque de recuperação. Preparar o finalizador do novo plano
   e confirmar que está efetivamente agendado para o regresso ao Linux.
7. Arrancar na manutenção independente. Confirmar que o disco interno não tem
   sistemas de ficheiros montados. Criar e verificar a imagem completa atual
   do SSD interno ANTES de reduzir o Linux ou sobrescrever qualquer região.
8. Montar apenas o Btrfs necessário, reduzir o sistema de ficheiros e confirmar
   o tamanho real. Desmontar e fechar o mapeamento LUKS. Gravar a imagem Windows
   preparada na nova posição e verificar integralmente o hash gravado. Aplicar
   a nova GPT e verificar setores, tamanhos, GUIDs e NTFS. Esta ordem é a do
   executor de 2026 e requer um plano revisto para a nova geometria.
9. Regressar ao Linux. Executar/verificar o finalizador adequado ao NOVO plano:
   validar o resultado e atualizar a geometria Windows nos registos APX v3 e
   os metadados antigos ainda usados. Remover o arranque temporário apenas
   depois das verificações. Não executar o finalizador de 2026 noutro plano.
10. Consultar o catálogo autenticado do Hub, confirmar os ambientes e testar
    abertura. Arrancar fisicamente no Windows, deixar concluir a verificação
    de disco prevista pelo redimensionamento e confirmar ficheiros e tamanho.
    Guardar evidência e atualizar o estado do projeto.

## Se os ambientes desaparecerem da lista

Nesta operação os dados dos ambientes continuavam no disco, mas o catálogo
falhava porque o registo Windows ainda indicava 120 GiB e a partição já tinha
170 GiB. O finalizador resolveu a divergência. Não recriar nem apagar ambientes
por causa de uma lista vazia: verificar primeiro o serviço e os metadados.

Comandos apenas de consulta, válidos se estes nomes ainda existirem:

```sh
lsblk -o NAME,SIZE,FSTYPE,UUID,PARTUUID,MOUNTPOINTS
systemctl status apx-environment-switch-v1.service
machinectl shell --uid=apx apx-hub /usr/bin/python3 /run/apx/environment-switch-client-v1.py catalog
```

## Evidência e código da operação concluída

No disco interno:
/var/lib/apx/backups/20261007T123224Z-windows-personal-grow-preflight/

Consultar plan-approved.json, gpt-before.*, firmware-before.txt,
prepare-windows-backup.py, prepare-grown-image.py, test-offline-pipeline.py,
build-maintenance.py, launch-grow.py, offline-grow.py, finalize-grow.py,
lab-result.json, build-result.json e finalized.json. Os scripts e as imagens
maintenance-grow/ e maintenance-recover/ são artefactos históricos vinculados
ao plano antigo; não são ferramentas genéricas de repartição.

No SSD externo, quando montado em /mnt/apx-backup:
/mnt/apx-backup/windows-personal-plus50-20261007/

- internal-ssd-before.raw: imagem completa original e manifesto de verificação.
- windows-current.ntfs.raw: Windows original de 120 GiB.
- windows-grown.ntfs.raw: imagem preparada de 170 GiB.
- plano, manifestos, offline-status.json e finalized.json.

A recuperação externa em /EFI/BOOT/BOOTX64.EFI pede RESTAURAR e verifica a imagem
completa antes de repor o disco. Essa recuperação repõe o estado ANTIGO; não a
usar para corrigir apenas a lista do Hub. Não desligar nem reutilizar o SSD
externo enquanto estiver a decorrer uma operação de manutenção.
