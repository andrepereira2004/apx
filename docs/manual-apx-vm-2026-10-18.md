# Teste manual do APX numa VM

A VM ficou guardada no Environment **Teste**, com Arch e APX instalados. Não é
a VM anterior, que foi removida no fim dos testes automáticos. Esta será mantida
até o utilizador acabar o teste e pedir a limpeza.

1. Volta ao Hub e abre novamente o **Teste** uma vez, para ativar a virtualização.
2. Abre o menu de aplicações e procura **Testar APX na VM**.
3. No primeiro arranque, escolhe no terminal uma palavra-passe só para a VM.
4. Entra no ecrã do APX da janela com essa palavra-passe e experimenta os menus,
   a criação de um Environment intermédio e a troca/regresso ao Hub da VM.

`Ctrl+Alt+G` liberta o rato/teclado. Usa **Desligar dentro da VM** para fechar
corretamente. A VM tem 4 GiB de RAM e quatro CPUs virtuais; não monta pastas ou
discos físicos do PC. O ficheiro `Testar-APX-na-VM.txt` no Teste repete as instruções.
A proteção de espaço pode parar só esta VM antes de consumir a reserva do PC.

O atalho foi validado e o QEMU tem SDL, OpenGL e VirtIO instalados no Teste.
O arranque, a entrada por palavra-passe através do teclado virtual, a descoberta
do rato/teclado e o movimento absoluto do rato foram verificados no convidado.
A instalação gráfica experimental precisou de uma vista udev só dos dispositivos
admitidos e de reservar a consola virtual 2; a consola 1 mantém recuperação.
O Hub permaneceu ativo por mais de dois minutos depois desta correção.
O lançamento interativo final com a palavra-passe do utilizador é o próximo passo.

A preparação e o login de teste usaram uma identidade sintética, sem exportar a
sua palavra-passe. Na primeira abertura pelo utilizador, o atalho define a nova
identidade apenas na VM e desativa o mecanismo inicial de autenticação de teste.
Este atalho/agente é um mecanismo do laboratório; não faz parte do instalador APX.
A VM contém o snapshot da interface anterior ao pedido dos ícones package; o
pedido dos ícones foi aplicado ao sistema físico conforme solicitado.

Evidência: `audit/2026-10-18-portable-manual/`. Não foi feito commit/push.
A limpeza futura é uma ação separada após o teste do utilizador; o helper
`scripts/portable/manual-vm-lab.py cleanup` remove o guardião e destrói apenas a
geração registada do Teste. Não o executar ao terminar a preparação.
