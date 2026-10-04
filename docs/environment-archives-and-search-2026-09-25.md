# Arquivos e pesquisa no gestor de ficheiros — 2026-09-25

## Âmbito e estado

Faculdade, Hytale, Minecraft e Steam são os quatro Environments Linux registados
com o módulo `files`. Os quatro receberam pacotes locais para criação/extração
de ZIP, TAR, 7z e leitura de RAR, pesquisa de ficheiros e miniaturas de vídeo.
As miniaturas de PDF já tinham `poppler-glib` instalado; a sua presença foi
confirmada. O Hub continua sem Thunar e não recebeu estes pacotes. O Windows
nativo usa um gestor de ficheiros separado e não foi alterado.

O Thunar já tinha File Roller e Tumbler. Foram instalados `thunar-archive-plugin`,
`xarchiver`, `7zip`, `unrar`, `unzip`, `zip`, `catfish` e `ffmpegthumbnailer`,
além das dependências `python-pexpect` e `python-ptyprocess` onde necessárias.
O pacote `tar` já existia. O plugin fornece ações de arquivo no menu de contexto;
Catfish é a pesquisa de ficheiros oferecida pelo Thunar quando presente.

O catálogo do módulo `files` no repositório e no runtime Host passou a incluir
estes pacotes e `poppler-glib` para novos Environments com esse módulo. A receita
da base comum não foi modificada; o Hub não herda estas extensões. A atualização
do módulo Host tem cópia e manifesto em
`/var/lib/apx/backups/20260925T182348Z-file-manager-features`.
Os presets `intermediate` e `complete` incluem `files`; a criação usa o catálogo
Host em cada execução. O runtime instalado ignora `nvidia-utils` e
`lib32-nvidia-utils` durante a atualização de pacotes da criação, antes de
instalar o artefacto NVIDIA alinhado à versão do módulo Host. Isto evita a
substituição temporária por uma versão incompatível. O ajuste preservou as
outras diferenças do runtime live e tem backup em
`/var/lib/apx/backups/20260925T183526Z-future-files-module-alignment`.

## Instalação e verificação

A primeira tentativa de atualização completa de Faculdade foi interrompida
durante o download, antes da transação, porque o plano incluía
`nvidia-utils 615.71.09` enquanto o Host e os Environments usam `610.43.03`.
O bloqueio de pacman remanescente foi removido após confirmar que não havia
outro processo de pacman. A instalação final limitou-se aos dez pacotes novos
resolvidos pela base atual, sem atualizar a pilha gráfica.

Faculdade, Minecraft e Steam receberam os pacotes por `systemd-nspawn` nos seus
roots parados, com a identidade de utilizador correta e o DNS do Host. Hytale
estava ativo: os mesmos pacotes Arch assinados foram copiados para o seu cache
local e instalados dentro desse Environment com `pacman -U`. Os registos estão
em `/var/lib/apx/backups/file-manager-*-install-20260925.log`.

Nos quatro Environments foram confirmados os executáveis, o plugin do Thunar,
os plugins de miniaturas de vídeo/PDF e a ausência de bibliotecas em falta no
plugin e no `ffmpegthumbnailer`. `nvidia-utils` permaneceu em `610.43.03-3`.
Num contentor Faculdade isolado, a criação e extração de ZIP, TAR e 7z
produziram ficheiros idênticos. O teste focal do catálogo e do gestor de
ficheiros passou (11 testes).

O menu do Thunar e as miniaturas reais ainda não foram observados numa sessão
gráfica. Um Thunar já aberto antes da instalação pode precisar de ser fechado e
aberto novamente para carregar o plugin. Os quatro roots de trabalho mantêm os
seus dados; a PEN USB e o Host não receberam pacotes por esta mudança.
Ainda não foi criado um Environment descartável novo para validar a instalação
física completa do catálogo; essa via foi verificada por leitura do runtime e
testes do plano de pacotes. Os pacotes futuros seguem as versões disponíveis no
repositório Arch na altura da criação, mantendo o mesmo conjunto de funções.
