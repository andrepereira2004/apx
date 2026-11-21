# Remoção Windows e integração Linux — 2026-11-21

O proprietário autorizou integrar apenas o Windows Faculdade retirado,
preservando Windows Pessoal. Foram instalados o novo estado pendente,
o adaptador de integração cifrada, o comando local e a apresentação do Hub.

- native-tests.log: 122 testes passaram.
- seed-tests.log: 8 testes passaram.
- qml-parser.log: parser qmlformat da sessão real passou sem diagnóstico.
- storage-lab.log: dois LUKS descartáveis; Btrfs com dados preservados após
  fechar/desbloquear e remontar; sem erros de dispositivos.
- gpt-roundtrip.log: GPT antes/depois escrita e relida em imagem esparsa;
  partições 1, 2, 3, 4 e 8 preservadas.
- boot-build.log: três UKIs construídas e assinaturas verificadas em namespace
  privado, sem escrever no arranque real. Artefactos descartáveis removidos;
  hashes e tamanhos em boot-image-evidence.json.
- deployment.log: backup e instalação de 18 ficheiros; sem alteração GPT/boot.

A integração física NÃO foi executada: falta palavra-passe em terminal local.
O próximo arranque após integração também requer confirmação física.
Uma falha antiga no teste de duplo clique do QML permanece (30/31 testes de
switch passam); já estava registada em CURRENT_HANDOFF antes desta tarefa.
Não houve commit/push. Ver docs/windows-delete-return-to-linux-2026-11-21.md.
