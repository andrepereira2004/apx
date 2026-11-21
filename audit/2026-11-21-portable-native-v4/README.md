# Windows portátil v4 — implementação nas fontes

Pedido: implementar para futuro PC; não instalar Windows neste computador.

Implementados preparação de ISO verificada e WinPE, executor de Recovery,
identidades por disco/partição, criação/ativação/arranque pelo Hub, retorno ao Hub
no Windows, retoma limitada e remoção/reclaim por instância. Provisionamento
incluído no instalador gráfico e no instalador de disco novo. O protocolo v3 do
cliente mantém compatibilidade, mas o adaptador portátil executa o ciclo v4.

Verificações locais exclusivamente de código: 71 contratos/testes unitários
passaram (24 de geometria/executor nativo incluídos); chamadas de hardware nos
contratos são simuladas. 33 fontes Python analisadas; 794 fontes do instalador
inventariadas, assets nativos presentes e pins da shell coerentes.

Sem ISO, VM, Windows, firmware ou bloco físico abertos para esta implementação.
Sem instalação de pacotes ou serviços do Host e sem qualquer deploy deste código
no piloto. Helper C conferido contra interfaces documentadas; não compilado nem
executado neste PC. Evidência de instalação da v3 anterior não certifica a v4.

Instruções, decisões e limites: `docs/portable-native-v4-development.md`.
Perfil futuro UEFI x64/GPT/Btrfs do instalador, ISO oficial e drivers próprios.
Nova criação por shrink recusa root multi-device; OOBE/licenciamento/BitLocker
não são automatizados. Nenhuma identidade/dado pessoal do piloto é exportado.
