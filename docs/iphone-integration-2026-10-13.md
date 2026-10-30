# Integração iPhone e Quality of Life — piloto de 2026-10-13

Estado mais recente: ver [localsend-network-2026-10-15.md](localsend-network-2026-10-15.md).
O toggle já existe e o aviso NetworkManager não impede o endpoint local mTLS.

## Atualização após manutenção autorizada

A recontagem foi autorizada e concluída; quotas consistentes e scrub completo
sem erros. LocalSend instalado na Faculdade e janela Wayland observada, mas
transferências não validadas devido à deteção de rede dependente de NetworkManager
e falta do IPv4 do iPhone. Nenhuma exceção de LAN aplicada. Detalhes atuais em
[system-health-2026-10-13.md](system-health-2026-10-13.md). O restante documento
preserva o diagnóstico e plano inicial anterior à instalação.

## Estado e autorização inicial

O proprietário aprovou o diagnóstico de estabilidade e a integração inicial de
LocalSend na Faculdade após a auditoria. Não autorizou a instalação automática
da lista completa. Não há LocalSend instalado nem exceção de rede aplicada nesta
fase. Recontagem de quotas e endereço IPv4 do iPhone foram solicitados; ambas
as respostas permanecem pendentes.

## Evidência física

- Host apx-host, Lenovo 82JU; Faculdade ativa, geração
  e9b08983-4740-4b85-8580-862c4a1d4c54, máquina apx-ge9b0898.
- Quotas Btrfs ativadas, modo qgroup; Inconsistent=yes, Override limits=no;
  nenhuma recontagem em curso. O serviço de armazenamento APX recusa corretamente
  publicar medições novas nesta condição. Não enfraquecer essa validação.
- Scrub anterior terminou em 2026-10-07 sem erros. Contador acumulado de
  corrupção 79; leitura/escrita/flush/generation=0. O registo do kernel consultado
  desde 2026-10-12 mostra o contador no arranque, sem novo erro de corrupção.
  Isto não constitui uma nova verificação integral dos dados.
- systemd-networkd-wait-online excedeu 120 s no arranque de 2026-10-12.
  eno1 está sem carrier e configuring; wlan0 routable/configured. As configurações
  en* e wl* usam DHCP e não declaram a Ethernet opcional para online. Trata-se da
  causa provável do timeout, sem ensaio de arranque nesta sessão.
- Faculdade tem namespace de rede privado e NAT. O filtro APX bloqueia tráfego
  de saída para endereços privados e siblings; não há encaminhamento de portas.
  A instalação de LocalSend isoladamente não permite transferências com o iPhone.

## Candidato LocalSend

Fonte: lançamento oficial v1.18.2,
https://github.com/localsend/localsend/releases/tag/v1.18.2

Arquivo LocalSend-1.18.2-linux-x86-64.tar.gz; SHA256 confirmado contra o digest do
asset publicado pela API GitHub:
287690a9a8eb6da9c83cc97b3e3030ac67daf32a7331fcf307d0939300658d16.

Preparação local em build/localsend-20261013, sem execução da aplicação.
O pacote final deve ser Environment-local e conter biblioteca Flutter, assets,
launcher, ícone e licenças. GTK3 já está na Faculdade; a biblioteca do tray pede
libayatana-appindicator, ainda ausente. Validar todas as bibliotecas dentro da
Faculdade, incluindo plugins carregados dinamicamente. Não instalar dependências
gráficas no Host. Não atualizar parcialmente bibliotecas base para instalar a app.

## Limites da integração proposta

1. LocalSend e respetiva configuração pertencem à Faculdade, sem copiar estado
   do Hub. Aceitação manual de ficheiros; sem autostart inicial.
2. Exceção de rede explicitamente opt-in, vinculada ao Environment, geração,
   interface ativa e dispositivo escolhido; nunca abrir toda a LAN.
3. Autorizar apenas a comunicação LocalSend necessária (porta padrão 53317),
   mantendo bloqueados Host, siblings e outros destinos privados. O IP é um
   limite de rede, não uma prova criptográfica da identidade do iPhone.
4. Começar pela ligação manual por IP, evitando retransmitir multicast para toda
   a rede. Para receber, validar um encaminhamento limitado ao iPhone autorizado
   e à sessão ativa, com remoção antes do teardown e atualização em nova sessão.
   Nada deste mecanismo está implementado neste documento.
5. Falha de validação ou mudança de identidade deve deixar o acesso fechado.
   Não publicar uma funcionalidade como pronta antes de validar lifecycle e
   ambos os sentidos da transferência.
6. Toggle futuro “Integração com iPhone/iPad”, desligado por defeito. Selecionar
   software não concede acesso à LAN automaticamente. KDE Connect, USB e iCloud
   serão opções separadas; não incluir iMessage/AirDrop nativo como promessa.

## Sequência e recuperação

- Antes de mutações físicas: autorização de recontagem, estabilidade das quotas,
  contadores/registo do kernel sem incremento e identificação APX válida.
- Se autorizado, recontar quotas existentes sem alterar limites, desativar quotas,
  eliminar qgroups ou snapshots. Confirmar Inconsistent=no e medições APX válidas.
- Para rede de arranque: preparar alteração estreita que torne só a Ethernet
  sem cabo opcional, com cópia da configuração original. Não reiniciar a rede
  ativa nem alterar iwd, drivers ou arranque para este diagnóstico.
- Preparar pacote, manifesto de hashes, inventário anterior e reversão exata da
  instalação. Snapshot apenas depois de validar quotas e a operação APX.
- Validar abertura Wayland, bibliotecas, integração APPS, serviço HTTPS e
  transferência de ficheiro sintético nos dois sentidos. Não tocar em documentos
  pessoais nem enviar conteúdo sem escolha do proprietário.
- Validar limpeza da exceção de rede, falha de arranque, mudança de geração e
  Hub→Faculdade→Hub sem deixar acesso ou serviços de partilha no Host.
- A reversão deve remover só o pacote/dependências acrescentados sem uso por
  outras apps, restaurar configurações alteradas e eliminar as regras próprias.
  Não restaurar um home completo por cima de trabalho novo do proprietário.

## Fontes

- https://github.com/localsend/localsend — rede, portais e distribuição.
- https://github.com/KDE/kdeconnect-ios — restrições de segundo plano/notificações.
- https://docs.syncthing.net/users/faq.html#is-there-an-ios-client — clientes iOS.
- https://github.com/BlueBubblesApp/bluebubbles-app — requisito de servidor Mac.
