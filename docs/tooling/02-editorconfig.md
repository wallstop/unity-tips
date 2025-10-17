# EditorConfig | Naming & Style Enforcement

**Website:** [Editorconfig](https://editorconfig.org/)

EditorConfig turns your style guide into automated IDE warnings. Pair it with CSharpier: the
formatter fixes whitespace, while EditorConfig keeps naming, braces, and other rules consistent
across the team.

## Starter `.editorconfig`

```ini
# Top-most EditorConfig file
root = true

[*]
charset = utf-8-bom
indent_style = space
indent_size = 4
trim_trailing_whitespace = true
insert_final_newline = true

[*.cs]
# Always use braces for control flow
csharp_prefer_braces = true:warning

# Interfaces: IPlayer, IEnemy
dotnet_naming_rule.interfaces_rule.severity = warning
dotnet_naming_rule.interfaces_rule.symbols = interface
dotnet_naming_rule.interfaces_rule.style = begins_with_i
dotnet_naming_symbols.interface.applicable_kinds = interface
dotnet_naming_style.begins_with_i.capitalization = pascal_case
dotnet_naming_style.begins_with_i.required_prefix = I

# Events: OnClick, OnPlayerDied
dotnet_naming_rule.events_rule.severity = warning
dotnet_naming_rule.events_rule.symbols = event
dotnet_naming_rule.events_rule.style = begins_with_on
dotnet_naming_symbols.event.applicable_kinds = event
dotnet_naming_style.begins_with_on.capitalization = pascal_case
dotnet_naming_style.begins_with_on.required_prefix = On

# Private fields: _health, _playerSpeed (_camelCase)
dotnet_naming_rule.private_fields_rule.severity = warning
dotnet_naming_rule.private_fields_rule.symbols = private_fields
dotnet_naming_rule.private_fields_rule.style = underscore_camel_case
dotnet_naming_symbols.private_fields.applicable_kinds = field
dotnet_naming_symbols.private_fields.applicable_accessibilities = private
dotnet_naming_style.underscore_camel_case.capitalization = camel_case
dotnet_naming_style.underscore_camel_case.required_prefix = _

# Public fields: health, playerSpeed (camelCase)
dotnet_naming_rule.public_fields_rule.severity = warning
dotnet_naming_rule.public_fields_rule.symbols = public_fields
dotnet_naming_rule.public_fields_rule.style = camel_case
dotnet_naming_symbols.public_fields.applicable_kinds = field
dotnet_naming_symbols.public_fields.applicable_accessibilities = public
dotnet_naming_style.camel_case.capitalization = camel_case

# Properties: Health, PlayerSpeed (PascalCase)
dotnet_naming_rule.properties_rule.severity = warning
dotnet_naming_rule.properties_rule.symbols = properties
dotnet_naming_rule.properties_rule.style = pascal_case
dotnet_naming_symbols.properties.applicable_kinds = property
dotnet_naming_style.pascal_case.capitalization = pascal_case
```

## Common Unity conventions to enforce

- Interfaces start with `I` (`IPlayer`, `IEnemy`).
- Events start with `On` (`OnClick`, `OnPlayerDied`).
- Type parameters start with `T` (`TComponent`, `TValue`).
- Private fields use `_camelCase` (`_health`, `_playerSpeed`).
- Public fields use `camelCase` unless Unity's serializer requires otherwise.
- Properties use `PascalCase` (`Health`, `PlayerSpeed`).
- Always include braces for `if`, `for`, `while`, etc.

## Next steps

The sample above covers the most common Unity conventions. For studio-wide enforcement, layer in
additional rules for analyzers, logging categories, filename matches, and namespace patterns. Treat
EditorConfig as executable documentation: if a style rule matters, encode it here so every IDE and
build machine agrees automatically.
