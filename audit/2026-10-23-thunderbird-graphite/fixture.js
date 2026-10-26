let {MailServices}=ChromeUtils.importESModule("resource:///modules/MailServices.sys.mjs");
let root=MailServices.accounts.localFoldersServer.rootFolder;
if (!root.containsChildNamed("Entrada")) root.createSubfolder("Entrada", null);
let folder=root.getChildNamed("Entrada");
if (!folder.getTotalMessages(false)) {
 for (let [n,subject] of ["Bem-vindo ao APX", "Documentos para a próxima aula", "Reunião de projeto"].entries())
 folder.QueryInterface(Ci.nsIMsgLocalMailFolder).addMessage("From - Fri Oct 23 10:00:00 2026\r\nFrom: Equipa APX <preview@example.invalid>\r\nTo: Preview <preview@example.invalid>\r\nSubject: "+subject+"\r\nDate: Fri, 23 Oct 2026 10:00:00 +0100\r\nMessage-ID: <preview"+n+"@example.invalid>\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\nMensagem fictícia para verificar apenas a aparência.\r\n");
}
let w=Services.wm.getMostRecentWindow("mail:3pane");w.document.getElementById("tabmail").currentAbout3Pane.displayFolder(folder);
return true;
