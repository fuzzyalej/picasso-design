# Migration

## Rules format

`design-system/rules.json` and the plugin's own `rules/core.json` both carry a
`picassoRulesVersion` field. The loader rejects a version it does not recognize
rather than guessing at its meaning, and falls back to the shipped rules.

### Version 1 — picasso 0.4.0

The initial format. A rules file is:

```json
{ "picassoRulesVersion": "1", "rules": [] }
```

Each entry in `rules` is a criterion: `identifier`, `title`, `statement`,
`level`, `category`, `verification`, and — for automated rules — `message`,
`check`, and `examples`. See `docs/reference.md` for the field reference.

No migration is required, because there is no earlier version.

## Artifact stamps

Generated artifacts carry a one-line provenance comment naming the picasso
version and rules format version that produced them. Nothing reads these yet;
they exist so a future version can recognize what it is looking at.
