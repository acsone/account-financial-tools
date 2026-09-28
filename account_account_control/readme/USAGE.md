When the modification reason is required, saving an account used in
posted journal entries, from its form or from the chart of accounts list
(including multi-edition), opens a pop-up asking for the reason of the
modification. The modification is only saved once a reason is selected.

The reason is logged in the chatter of the account with the tracked
changes.

For developers: the reason is given to `write()` through the
`modification_reason_id` value. Writes done as superuser (`sudo()`) or
with the `skip_account_modification_reason` context key (e.g. technical
updates of the chart of accounts) do not require a reason.
