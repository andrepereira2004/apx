# Partilha e wallpapers — 2026-11-21

Instalado no piloto Lenovo 82JU, com seis homes registados e semente independente.
Fotografias foi renomeada pelo broker para wallpaper; nove JPG preservados.
A partilha continua montada só de leitura. A ação Thunar «Mudar nome na Partilha…»
usa o broker: apenas nomes no mesmo diretório, caminhos relativos ancorados por
descritores, sem seguir links nem substituir destinos existentes. O socket oculto
na própria partilha permite reconectar depois de reiniciar o broker, evitando
referências antigas de sockets montados individualmente nas sessões abertas.

O broker publica a cada dois segundos um índice mínimo de nomes de fotografias
em uso e Environments registados. Reconhece o hash da cópia local escolhida,
incluindo importação WebP convertida, sem partilhar os homes ou configurações.
Environments desligados contam; imagens antigas em cache não contam. A coluna
«Wallpaper em uso» aparece na lista detalhada Thunar e no seletor GTK dentro de
/home/apx/Partilha/wallpaper. Mostra ✓ e os nomes, sem impedir reutilização.
O índice revelou IMG_1134.JPG já usada por financas e hub.

Zoom/posição conservam o valor pendente durante a gravação e só o libertam se
não chegou uma alteração posterior. QuickShell recarregou o componente às 16:03.
Teste Qt 6 de duas mudanças rápidas com gravação atrasada passou: não volta aos
100% durante a primeira gravação e preserva os 160% perante a resposta dos 120%.

Validação: dois testes novos do broker, oito testes seed, compilação GTK chooser
com -Wall -Wextra -Werror, parser QML e teste Qt (3 PASS incluindo init/cleanup).
Renomeação real de pasta descartável a partir da sessão Finanças passou; fixture
removido. Seletor GTK real e Thunar real confirmaram cinco linhas com check entre
nove fotos; evidência em thunar-checks.txt, usage.ini e zoom-test.log.
A aceitação física do gesto rápido pelo proprietário continua por observar.

A bateria antiga test_apx_appearance.py tem duas falhas e um erro em contratos
anteriores de cor/destinos e assinatura apply_theme; test_apx_appearance_opacity.py
tem dois erros por exigir o helper de lock em /home/apx do Host. O helper de
aparência não foi alterado nesta tarefa; estas baterias não ficam declaradas verdes.

Backups e inventários de substituição:
- /var/lib/apx/backups/20261121T160301Z-wallpaper-sharing
- /var/lib/apx/backups/20261121T160533Z-wallpaper-sharing

Fonte, homes, semente e pins dos assets alterados sincronizados. Manifesto native
continua enabled=true, sem erros; nenhum ficheiro coberto por ele foi alterado.
Nenhum commit/push. Testes e depuração temporários removidos após guardar evidência.
