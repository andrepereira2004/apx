/* Native MailExtension APIs only. No message body reads, host permissions or
 * message sending/deleting. Closing explicitly clears selection so selecting
 * the same message again works, and a closed message is not restored on restart. */
const closing = new Set();

async function closeMessage(tab) {
  if (tab.type === "messageDisplay") {
    await browser.tabs.remove(tab.id);
    return;
  }
  if (tab.type !== "mail" || closing.has(tab.id)) return;
  closing.add(tab.id);
  try {
    await browser.mailTabs.setSelectedMessages(tab.id, []);
    await browser.mailTabs.update(tab.id, { messagePaneVisible: false });
  } finally {
    closing.delete(tab.id);
  }
}

browser.messageDisplayAction.onClicked.addListener(tab => {
  closeMessage(tab).catch(error => console.error("APX: could not close message", error));
});

browser.mailTabs.onSelectedMessagesChanged.addListener((tab, selection) => {
  if (!closing.has(tab.id) && selection.messages?.length) {
    browser.mailTabs.update(tab.id, { messagePaneVisible: true })
      .catch(error => console.error("APX: could not reopen reading pane", error));
  }
});
