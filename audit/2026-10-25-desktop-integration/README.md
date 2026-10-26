> Atualização do proprietário: Thunar é e deve continuar a ser o gestor de
> ficheiros predefinido. A classificação abaixo como problema foi retirada.
> Candidato revertido no repositório, incluindo hashes e testes específicos;
> nunca foi aplicado ao sistema. Inventário permanece válido como observação.

# Integração APX — inventário inicial e primeira correção

Inspeção física apenas de metadados de pacotes/configuração. Sem abrir apps,
ler documentos, notificações ou títulos de janelas; sem alterar sessões.

| Environment | Ficheiros | Brave | Thunderbird | ZapZap | Flatpak apps |
| --- | --- | --- | --- | --- | --- |
| faculdade | 4.20.10-1 | 1:1.95.101-1 | 155.0.1-1 | 7.5.1-1 | nenhuma encontrada |
| hub | não encontrado no inventário de pacotes | 1:1.93.136-1 | não encontrado no inventário de pacotes | não encontrado no inventário de pacotes | nenhuma encontrada |
| hytale | 4.20.10-1 | 1:1.96.59-1 | não encontrado no inventário de pacotes | não encontrado no inventário de pacotes | com.hypixel.HytaleLauncher |
| minecraft | 4.20.10-1 | 1:1.95.101-1 | não encontrado no inventário de pacotes | não encontrado no inventário de pacotes | nenhuma encontrada |
| steam | 4.20.10-1 | 1:1.95.101-1 | não encontrado no inventário de pacotes | não encontrado no inventário de pacotes | nenhuma encontrada |

Pacotes ausentes não provam ausência de uma instalação manual. Nenhuma app
Electron empacotada foi identificada por nome de pacote; runtimes integrados
não são classificados por este inventário. Wayland/XWayland, foco, diálogos,
notificações e desempenho por app continuam não testados.

## Primeiro problema confirmado no código instalado

Nos cinco homes, o helper de ativação repõe a associação de diretórios para
Thunar sem consultar a preferência existente. Preparada correção no repositório:
preservar uma associação existente, inicializar Thunar apenas se faltar e
reportar falha de inicialização. Não aplicada ao sistema nem aos homes/seed vivos.
Hashes do modelo no runtime e respetivo pin de recuperação atualizados no repo.

Validação: 4 testes comportamentais de associação passam; sintaxe Bash passa;
7 testes de seed passam após atualizar os hashes. A suite work-defaults tem
12/14 testes a passar: duas falhas em expectativas de barra/controlos existentes,
sem alteração desses ficheiros nesta etapa. Não representam validação gráfica.

## Próxima experiência proposta

Faculdade contém as quatro aplicações prioritárias e só esse container estava
listado em execução na observação. Usar ficheiros descartáveis para comparar
abrir/guardar no Brave e anexar no Thunderbird, sem enviar. Confirmar filtros,
cancelamento, foco, geometria e teclado. Só depois escolher ajustes visuais;
a configuração de um portal não demonstra que cada app o utiliza corretamente.

Não houve pacote instalado, serviço reiniciado, deploy, commit ou push.


## Segunda etapa — teste físico do seletor e integração LocalSend

Executado `chooser-probe.py` na sessão Faculdade por `session-command.py`, com
GTK_USE_PORTAL=1. Janela GTK3 descartável e pasta temporária vazia, removidas ao
terminar. Duas operações: abrir e guardar, fechadas automaticamente por hide/
destroy, sem selecionar nem guardar ficheiros. O teste mostrou o diálogo GTK
flutuante em Wayland, foco no diálogo durante abertura e retorno à janela de
origem após fecho. Posição/tamanho da janela de origem constantes em ambas as
operações. Isto não valida cancelar pelo teclado/botão, filtros na seleção real,
arranque de Brave/Thunderbird nem fluidez percebida. Zero janelas de teste no fim.
A janela temporária entrou no layout durante o teste; nenhuma janela do dono foi
fechada, controlada ou inspecionada quanto a conteúdo. Evidência: chooser-live.json.

O teste revelou aviso de permissão na entrada de LocalSend. Confirmado ficheiro
regular `/usr/share/applications/org.localsend.localsend_app.desktop` no root
privado de Faculdade com modo0600, ilegível pelo utilizador da sessão. Alterado
apenas modo para0644; hash do conteúdo e proprietário mantidos. Gio reconhece
agora a entrada; Thunar continua predefinido. A aplicação não foi iniciada.
Inventário/recuperação: localsend-permission-fix.json; validação:
localsend-validation.json. Reversão: repor0600 no caminho exato registado.
Origem do modo incorreto ainda não determinada; reinstalar/recriar o pacote pode
reintroduzi-lo. Não foi alterado o artefacto distribuído nem outros Environments.

Próximo: validar o mesmo percurso por aplicação com perfis/ficheiros descartáveis,
e rastrear o empacotamento LocalSend antes de generalizar a correção. Não há
justificação nesta amostra para substituir o seletor existente.
