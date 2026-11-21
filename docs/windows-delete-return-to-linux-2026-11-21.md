# Windows secundário: apagar devolve o espaço ao Linux

## Objetivo autorizado

Em 2026-11-21 o proprietário esclareceu que apenas Windows Faculdade
(`windows-testes`, geração `2770478b-480f-4aea-8910-e3201d5334c5`) deve ser
removido. Windows Pessoal fica preservado. O destino pretendido do espaço é o
Linux atual, e este passa a ser o resultado esperado de Apagar Windows.

## Desenho implementado para o piloto

A remoção secundária deixa de terminar com um slot reutilizável Windows.
Depois de limpar p5/p6 e retirar a inscrição, fica pendente
`awaiting-linux-auth`. O Hub oferece Terminal do Host e o comando curto
`apx-concluir-remocao-windows`. A palavra-passe de cifragem é introduzida nesse
terminal, com eco desativado, e validada contra p2. Nunca é aceite pelo chat,
contrato APX, argumentos de processo, logs ou ficheiros de chave.

O adaptador é específico do SSD/Lenovo atual. Consolida os extents contíguos
p6/p7/p5 numa nova p5 Linux LUKS2 de 77,515625 GiB, preservando os UUIDs e
extents exatos de p1/p2/p3/p4/p8. A nova cifragem usa a palavra-passe existente
e torna-se um segundo membro do Btrfs raiz. Não move Windows Pessoal nem
altera o início/tamanho de p2. Não se introduz volume de ficheiros separado.

Antes da alteração GPT, prepara e verifica as três UKIs assinadas: normal,
Nouveau recovery e IOMMU. Todas passam a esperar explicitamente pelo novo
desbloqueio antes de montar sysroot. A recuperação Nouveau mantém módulos
amdgpu/nouveau separados. As UKIs só são substituídas depois de o volume
cifrado existir e estar desbloqueado; o membro só é acrescentado ao Btrfs
depois de todas as UKIs estarem instaladas. Não reinicia automaticamente.

Só depois de confirmar o membro no Btrfs elimina a autoridade de reutilização
Windows e o ícone da geração retirada, grava um recibo Linux e publica
`complete`. Conservam-se registos históricos e backups de recuperação do
Host; não se promete ausência de todas as referências históricas nem
apagamento forense do SSD. A capacidade útil acrescida é ligeiramente menor
que o extent físico devido ao cabeçalho LUKS e metadados Btrfs.

## Falhas e limites

Planos root-owned com hash e GPT integral permitem repetir o mesmo comando
depois de interrupção. Antes da alteração GPT, falhas restauram apenas as
configurações preparadas, com as UKIs originais intactas. Depois de alterar
GPT, o estado permanece pendente e a repetição exige a tabela exata antes ou
depois da operação e a mesma identidade LUKS. Não se faz rollback automático
após acrescentar o membro: ambos passam a ser necessários para montar a raiz.

A remoção do Windows original continua recusada pelo executor v3 existente;
esta tarefa não autoriza removê-lo. Este adaptador não é um gestor genérico
de partições, não é produção e não implementa a operação inversa de retirar
capacidade do Btrfs para criar outro Windows. Não reutilizar o checkpoint
Windows antigo como autorização de novo layout depois de integrar o espaço.

## Evidência e estado físico

Evidência em `audit/2026-11-21-windows-linux-reclaim/`:
testes de plano/identidade e remoção/reentrada; GPT antes/depois escrita e
relida numa imagem esparsa descartável; dois volumes LUKS em loop, adição
Btrfs, fecho/reabertura e remontagem com dados anteriores preservados; build
real e verificação criptográfica das três UKIs num namespace de mounts privado.

Esses testes não escrevem nas partições físicas nem validam um reboot real.
No fim desta preparação, a integração física permanece por executar com a
palavra-passe local. Depois é necessária confirmação do próximo arranque.
Sem commit/push. As alterações anteriores do working tree foram preservadas.

## Correção do gate de saúde

A verificação inicial recusava qualquer contador acumulado. O histórico 79 de
corruption_errs já era conhecido e voltou a ser observado sem novos erros num
scrub só de leitura de 159,18 GiB em 21/11. A implementação usa agora uma prova
root-owned desse scrub, válida por 24 h, ligada à raiz, aos contadores exatos
e ao último scrub. Não repõe contadores nem aceita erros adicionais. O comando
instalado chegou ao pedido da palavra-passe num PTY e foi cancelado sem a
introduzir. A integração permanece pendente do passo local do proprietário.

## Integração física concluída

O proprietário executou o passo local. Confirmados dois membros no APX_ROOT,
77,5 GiB adicionais cifrados, cerca de 294 GiB totais e 130 GiB disponíveis.
Windows Pessoal e Recovery preservados; pending/free-slot removidos. O primeiro
arranque com as novas imagens ainda requer validação física.

## Pré-verificação de arranque e correção de assinatura

A validação autorizada encontrou objcopy a reescrever o input durante
--dump-section. Corrigido para OUTPUT descartável, com teste de regressão, e
refeitas as três UKIs. Confirmadas assinaturas após cópia para EFI e hashes
inalterados por inspeção. Um coletor pós-reboot foi instalado para registar
um boot_id diferente, os dois membros, Windows Pessoal e estado de saúde.
O resultado físico permanece pendente até ao próximo desbloqueio/arranque.

## Arranque real validado

O proprietário confirmou o arranque e o coletor passou num boot_id novo.
Ambos os volumes cifrados montaram na raiz Btrfs, Hub gráfico ativo, 294 GiB
totais e cerca de 129 GiB livres. Windows Pessoal, assinaturas e contadores
verificados, sem unidades falhadas. O coletor temporário foi retirado; recibo
preservado no Host e na evidência do repositório.
