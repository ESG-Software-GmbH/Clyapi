# AGENTS.md

Clyapi — Python wrapper for the Climcycle API. See README.md for full docs.

## You may do this

- Clone the repo and `cd` into it (`git clone https://github.com/ESG-Software-GmbH/Clyapi && cd Clyapi`)
- Create/activate the virtualenv
- Install locally from the repo root: `pip install -e .`
- Write and run code against `clyapi` (see README "Usage" and `examples/`)

Work from the repo root so you can read this `AGENTS.md` and the `skills/`
directory.

## You must not do this

Credentials are set by the human operator, always.

- Do NOT create, read, open, edit or inspect `~/.clyapi/config.json`
- Do NOT ask the user to paste secrets into the chat
- Do NOT write `Client_Application_Id` or `Client_Secret` values anywhere —
  not into code, notebooks, `.env` files, or this repo
- Do NOT continue past the credential step on your own

## The credential step

After `pip install -e .` succeeds, stop. Print the block below to the user
verbatim, then wait for them to confirm they are done.

---
**Set up your Climcycle credentials**

Open a terminal and run:

```
mkdir -p ~/.clyapi
nano ~/.clyapi/config.json
```

Paste this, replacing the placeholders:

```json
{
  "Institution_Configs": {
    "Prod": {
      "Your Institution": {
        "Client_Application_Id": "application uuid",
        "Client_Secret": "secret uuid"
      }
    }
  }
}
```

Use `"Preprod"` instead of `"Prod"` for the preprod environment. The
institution name can be anything, but use the same name as in the
Climcycle app. Find both UUIDs under **Secret Management** in the
Climcycle app — you need the User Admin role.

Tell me when you've saved the file.

---

## Verifying

Once the user confirms, check the connection:

```python
import clyapi
client = clyapi.client.Client("<institution name the user gave you>")
print(clyapi.endpoints.institution.institution_info(client))
```

If this fails, report the error and hand back to the user. Do not try to
repair the config file yourself.