# Revisão de ferramentas de apoio — 2026-10-22

Inspeção da instalação Minecraft, das entradas desktop, documentação instalada,
dependências obrigatórias da base pacman e configuração APX. As conclusões não
provam utilização habitual pelo utilizador. Não houve novas desinstalações.

| Ferramenta | Evidência / função | Decisão proposta |
|---|---|---|
| Catfish | Programa separado. O binário Thunar contém a opção “Search with Catfish…” e o erro correspondente. Nenhum pacote instalado o exige. Não foi encontrada uma chamada personalizada nos atalhos/pesquisas de configuração inspecionados. | Opcional. Pode ser desinstalado se não se usa a pesquisa externa do Thunar; navegar em pastas e a pesquisa Rofi são independentes. Perde-se a pesquisa específica do Catfish. |
| uuctl | A entrada desktop diz “User unit manager”; a documentação instalada do uwsm descreve-o como ferramenta opcional para gerir unidades de utilizador. Faz parte de uwsm, não é um pacote independente. | Não é necessário para atualizar software. Corrigido o rótulo errado para “Serviços da sessão (uuctl)”. Não remover uwsm apenas para eliminar esta entrada. |
| Atualizações APX | apx-settings oferece “Abrir atualizações APX”, através do cliente coordenado ou apx-environment-update-v1. | Manter o caminho de atualizações APX; não confundir com uuctl. |
| File Roller | Manipula arquivos; o plugin de arquivos do Thunar tem adaptador org.gnome.FileRoller.tap. | Manter para compressão/extração e mover para Sistema, conforme pedido. |
| gpsd / xgps / xgpsspeed | Waybar exige gpsd como dependência obrigatória nesta instalação. | Manter o pacote e as entradas visíveis. A utilidade de localização das interfaces não significa que se possa apagar a biblioteca exigida. |
| CUPS / configurar impressoras | cups não tem dependentes obrigatórios nesta instalação; fornece o serviço de impressão. | Opcional conforme necessidade de impressão. Mantido: não foi decidido abdicar da impressão. libcups é separado e é usado por outras aplicações. |
| qv4l2 / qvidcap | Pertencem a v4l-utils. ffmpeg, gst-plugins-good e sane dependem desse pacote. | Interfaces opcionais de diagnóstico/captura; preservar o pacote exigido. |
| Descoberta Avahi / SSH / VNC | Interfaces pertencem a avahi. libcups, pipewire-pulse, ostree, sane e outros exigem avahi nesta instalação. | Interfaces dispensáveis para uso diário; preservar pacote e entradas visíveis. |
| Topologia de hardware | lstopo pertence a hwloc; onetbb, openpmix, prrte e openmpi exigem hwloc. | Ferramenta de diagnóstico; preservar pacote exigido. |
| Preferências do Thunar / temas Rofi | Configuração de programas existentes. | Manter em Sistema. Não apagar Thunar/Rofi para retirar opções de configuração. |
| Mousepad / mpv / Ristretto | Editor de texto, leitor multimédia e visualizador de imagens locais. | Opcionais, mas funções distintas; não são redundantes com a navegação de ficheiros. Manter até decisão sobre essas funções. |

Alteração aplicada na source, seed independente e cinco homes: File Roller
em Sistema e rótulo correto do uuctl. 40 testes do catálogo e sete testes da
seed passam; deployment recheck sem alterações pendentes. Backup:
/var/lib/apx/backups/20261022T201641Z-controls-followup.
