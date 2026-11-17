# Dispositivos desmontados no seletor — 2026-11-16

O proprietário pediu que os dispositivos aparecessem na própria janela de abrir/guardar usada pelo Bedrock e Brave, e autorizou alterações no sistema.

Causa reproduzida na sessão Minecraft: GIO lista a pen FAT UUID 4079-3F8D como «1.0 GB Volume», ainda desmontada, com can_mount=1. A linha nativa GTK tem section-type=2, place-type=3 e URI nulo. O filtro APX exigia URI e ocultava-a. A pen Ventoy anteriormente autorizada na ponte não está ligada; não se modificou essa política nem se criaram marcadores permanentes.

Correção: conservar também as linhas nativas de volume/dispositivo nessa secção, mantendo os restantes filtros. GTK continua responsável pela ativação e montagem. Compilação -Wall -Wextra -Werror, exceto parâmetros de callbacks já existentes. Fonte/módulo instalados na semente independente e cinco homes; pins dos runtimes e digest de recuperação sincronizados. Backup /var/lib/apx/backups/20261116T193621Z-chooser-unmounted-devices (15 ficheiros).

Validação: before.log reproduz child_visible=false em Open e Save; after.log e installed.log confirmam child_visible=true, cabeçalho Dispositivos e lookup dos botões de resposta. portal-check.py abriu pedidos reais OpenFile/SaveFile no backend recarregado, capturou open.png/save.png e fechou apenas os próprios pedidos. Ambas as capturas mostram a pen na barra lateral. Não foi realizado upload/download no Brave nem montagem da nova pen: a validação cobre a apresentação pedida, não o acesso ao conteúdo. Só o backend GTK foi reiniciado, sem reiniciar o launcher. Nenhum ficheiro do proprietário foi importado/guardado. Sem commit/push.
