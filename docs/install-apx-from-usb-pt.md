# Instalar APX num PC sem sistema

Não é necessário instalar o Codex. O ponto de partida é uma pen de instalação
oficial do Arch Linux x86_64, com acesso à internet, e o pacote de fontes APX
preparado neste projeto. O instalador é experimental.

Requisitos deste percurso: PC x86_64, um disco vazio de pelo menos 160 GiB,
arranque UEFI ou BIOS e Secure Boot desativado. Não configura encriptação nem
instala Windows. Recusa discos com partições ou assinaturas de dados; não apaga
automaticamente um sistema existente. A seleção de drivers usa os componentes
detetados, sem uma lista de modelos de computador autorizados.

Arranca pela pen do Arch e liga à internet. Leva o pacote APX numa unidade de
dados acessível ou transfere-o para o ambiente de instalação. Como root:

```sh
tar -xzf /caminho/APX-instalar-PC-vazio-20261018.tar.gz
cd apx-portable
sha256sum -c SHA256SUMS
python scripts/portable/install_apx_disk.py --list-disks
```

Escolhe o disco pelo caminho, tamanho e modelo apresentados. Substitui o exemplo
abaixo pelo disco correto; não copies literalmente `/dev/DISCO`:

```sh
python scripts/portable/install_apx_disk.py --disk /dev/DISCO --apply
```

O script apresenta o plano e pede uma frase de confirmação específica para esse
disco. Depois muda explicitamente o teclado da consola para português e pede uma
palavra-passe nova de recuperação para o utilizador técnico `root`.

Instala Arch, Btrfs, o arranque, firmware, microcódigo e os drivers selecionados.
No fim, desliga o PC, retira a pen de arranque e arranca pelo disco instalado.
O APX continua a instalação automaticamente e pede a tua palavra-passe APX nova.
A consola e a interface usam o mesmo teclado português, incluindo símbolos.

Com rede por cabo, a ligação é automática. Se precisares de configurar Wi-Fi
nesse primeiro arranque, usa Ctrl+Alt+F3, entra como `root` com a palavra-passe de
recuperação e executa `nmtui`. Regressa com Ctrl+Alt+F1. Credenciais Wi-Fi deste
PC não são copiadas para o novo.

Quando terminar, aparece o login gráfico do APX. Nos arranques seguintes, entra
normalmente; o instalador não volta a executar. Cria depois os teus Environments
no Hub. Aplicações pessoais, documentos, biometria e os dados dos Environments
antigos não fazem parte deste pacote de instalação limpa.

Se a instalação APX falhar, a repetição automática fica desativada para preservar
o estado parcial. Usa a consola de recuperação e consulta os checkpoints em
`/var/lib/apx/portable-install.json` e `portable-graphical-install.json` e
`journalctl -u apx-first-boot -b`. Não voltes a formatar um disco com dados para
contornar uma mensagem de erro.

O suporte continua a depender do hardware suportado pelo Arch e pelos drivers.
Um GPU NVIDIA ausente da lista oficial da versão do driver é recusado antes de
alterar o disco. Os testes em VM não substituem uma instalação de validação em
cada família de hardware real. Limites técnicos e evidência datada:
`empty-disk-install-v1.md` e `empty-disk-validation-2026-10-18.md`.
