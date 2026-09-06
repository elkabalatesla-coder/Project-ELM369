# Bo Communications Assistant

Issue #16 / BO-COMM. Drafts SMS, email, and phone scripts for Project ELM369.

**Hard rule: never sends.** No SMS, email, ADB, telephony, or satellite actuation.

Vault IDs: primary `JMR08241978202646902` · companion `JMR0824197846902`  
Provenance footer: Kokomo IN 46902 · Joseph Michael Rose · IX JR · 🌹

## Commands

```bash
# Single-turn draft
python3 -m tools.bo_assistant draft "When is my appointment?" --channel sms --tone corporate

# Email draft
python3 -m tools.bo_assistant draft "Confirm receipt of filing packet" --channel email --tone government

# Phone script (never auto-dials)
python3 -m tools.bo_assistant draft "Walk through status update" --channel phone --tone formal

# Multi-turn template with prior thread
python3 -m tools.bo_assistant multi-turn "Can you reschedule?" \
  --prior-turns '[{"role":"user","content":"I need help"},{"role":"assistant","content":"Happy to help — what do you need?"}]'
```

## Safety

| Action | Allowed? |
|--------|----------|
| Compose draft text | Yes |
| Include Kokomo provenance footer | Yes |
| Transmit SMS / email / phone | **Never** |
| ADB / satellite / modem control | **Never** |

## Tests

```bash
python3 -m unittest tools.bo_assistant.tests.test_draft -v
```
