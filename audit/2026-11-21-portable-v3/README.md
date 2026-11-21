# Ensaio portátil v3 — 2026-11-21

Instalação limpa com 780 fontes verificadas: 16 verificações passaram;
novo arranque independente: 15 verificações passaram. Evidência final em
`replay3/install-result.json`, `replay3/result.json`, `replay3/cold-boot.json`,
`replay3/source-verification.json` e `replay3/source-manifest.json`.
Partilha mediada e DNS privados exercitados em `replay3/shared-and-dns.json`.
Captura inspecionada visualmente: `replay3/control-centre.png`.

Os dois ensaios anteriores preservam diagnóstico: dependência facial retirada
indevidamente exigida e cache de pacotes sem acesso no namespace. Corrigidos
manifesto/dependências, modo público dos pacotes e bind idmap. Acrescentado
proxy DNS HTTPS limitado por veth, sem abrir serviços do Host/LAN aos workloads.

62 testes portáteis passaram. A seleção alargada executou 418 testes com sucesso,
com seis falhas antigas excluídas e discriminadas em `source-tests.json`.
Planeador nativo: 15 testes; serialização GPT exercitada com sfdisk em ficheiros
esparsos para SATA/virtio/NVMe e setores 512/4096 (`native-sfdisk-roundtrip.json`).

O planeador nativo v4 é apenas de leitura (`executable=False`). Identidades,
transações e planos de reclaim não constituem executor offline, WinPE ou
instalação Windows funcional. Aceitação humana/física e paridade total pendentes.

Laboratório descartável `codex-test-portable-v3`, geração registada em
`intent.json`, limitado a 24 GiB agregados e guarda de 97 GiB livres. Reserva
produto 96 GiB inalterada. QEMU/pacotes apenas no Environment próprio; nenhum
bloco físico, home ou credencial do Host entrou na VM. Kernel/partições/boot do
Host não alterados. Unidades, lease, qgroup e Environment removidos;
`cleanup.json` confirma outros registos intactos e espaço recuperado.
A fixture DNS de laboratório não integra as fontes do produto.
