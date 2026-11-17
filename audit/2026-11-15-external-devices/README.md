# Dispositivos externos e Extrair aqui — 2026-11-16

O proprietário pediu a pen USB em Dispositivos e a correção de «Extrair aqui»
para futuras extrações. No piloto, os ficheiros da pen são entregues por uma
ponte de montagens, sem entregar o dispositivo de blocos ao Environment.

O patch Thunar classifica os marcadores dinâmicos sob `/media/apx-usb/` no grupo
de montagens de Dispositivos, com ícone USB. Mantém esses marcadores tanto na
recarga como na gravação da lista; continuam sem operação local de ejetar.
O seletor GTK usa o mesmo grupo visual e ícone. A política de montagem continua
limitada à identidade USB já autorizada; não foi ampliada a outras unidades.
Os quatro binários Thunar e o módulo/semente GTK foram instalados com backup
`/var/lib/apx/backups/20261115T235340Z-external-devices`.

O plugin de arquivos do Thunar 0.6.0 consulta `g_app_info_get_all_for_type` em
`tap_backend_mime_applications`, em vez de confiar apenas no aplicativo padrão.
Fonte consultada: https://gitlab.xfce.org/thunar-plugins/thunar-archive-plugin/-/raw/thunar-archive-plugin-0.6.0/thunar-archive-plugin/tap-backend.c
Antes da correção, `gio mime application/zip` mostrava File Roller como padrão,
mas nenhuma aplicação registada/recomendada. Após acrescentar as associações
explícitas a `[Added Associations]`, regista e recomenda File Roller.
Corrigidos 17 tipos de arquivos nos quatro homes com gestor de arquivos e na
semente independente; preferências existentes preservadas. Pins do runtime e
da recuperação sincronizados. Backup:
`/var/lib/apx/backups/20261115T235852Z-archive-associations`.

Validação:

- Thunar e módulo GTK recompilados; módulo compilado com `-Werror`.
- Patch nativo completo revertido/reaplicado numa cópia temporária: 14 fontes
  coincidem byte a byte com a árvore compilada.
- Seis testes Python de disponibilidade da pen e serviço Host passaram.
- `check-thunar-devices.c`: entrada única com grupo 512 e ícone USB; remoção
  e reinserção do marcador na configuração isolada atualizam a lista sem duplicar.
- `check-chooser-devices.py`: entrada única sob Dispositivos e navegação real
  através de `row.activate` para a pen. Emitir diretamente o sinal interno
  `row-activated` não reproduz a ativação GTK e foi retirado do teste.
- `check-archive-action.c`: invoca as duas ações `Tap::extract-here` do plugin
  real sobre ZIP e TAR de teste, e verifica o conteúdo extraído. Passou.
- Captura real `devices-final.png`: Thunar em português, PEN USB sob
  Dispositivos; Downloads mantido no workspace 4.

Antes de o proprietário esclarecer que pretendia reparar a ação, executou-se
indevidamente a extração do seu Backup.zip. O proprietário autorizou conservar
o resultado. Downloads/Backup contém os 58 286 ficheiros esperados, sem
ficheiros ausentes nem tamanhos divergentes; não foi calculado CRC completo.
A correção das associações é independente dessa extração e foi testada com
arquivos pequenos descartáveis. O arquivo original foi preservado.

Não houve alteração de discos, serviço de montagem, pacotes ou permissões de
acesso USB. Sem commit/push.
