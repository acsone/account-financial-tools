This module adds controls on the accounts, for management control and
auditability purposes:

- **Code lock**: the code of an account used on at least one journal item
  of a posted journal entry cannot be changed (optional).
- **Label uniqueness**: two accounts sharing a company cannot have the
  same label (optional).
- **Modification reason**: any modification of an account requires a
  reason, selected from a configurable list. The reason is stored on the
  account and tracked, so it is logged in the chatter together with the
  other tracked changes.
