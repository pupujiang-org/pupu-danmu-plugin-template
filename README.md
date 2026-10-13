# Pupu Danmu official plugins

This public repository contains source for **data-only** official Pupu Danmu plugins and the tooling that packages immutable ZIP assets for GitHub Releases.

The host repository owns runtime behavior, permissions, session pins, model access, pacing, and the final send decision. A plugin package cannot contain or execute Python, JavaScript, WebAssembly, native libraries, installation hooks, or arbitrary UI. Plugin resources are untrusted data and never override host safety rules.

## Repository layout

- `plugins/<slug>/`: one plugin's manifest, static JSON/text resources, documentation, and the MIT license shipped inside the package.
- `schemas/manifest.schema.json`: the reviewed schema-v1 shape. The host parser remains the installation authority.
- `scripts/package_plugins.py`: deterministic static ZIP packaging; it does not import or execute plugin contents.

The independent [plugin registry](https://github.com/pupujiang-org/pupu-danmu-plugin-registry) stores Catalog metadata and publishes the generated Pages index. It must never contain plugin source or ZIP packages.

## Local validation and packaging

Use Python 3.13 or newer:

```powershell
python scripts/package_plugins.py --check
python scripts/package_plugins.py --plugin fabric-buyer --output dist
```

The package contains only the files declared by the static allowlist and manifest. The command prints the resulting ZIP path and SHA-256. No plugin code runs during validation, packaging, install, or use.

`--check` and packaging also enforce the license policy, so a wrong license fails the command and the `Validate plugin packages` workflow instead of being caught in review:

- every official plugin manifest must declare `"license": "MIT"`;
- every plugin `LICENSE` file must be the MIT text and is packaged into the ZIP;
- the repository root `LICENSE` must be the same MIT text.

## Releases

After review, publish a plugin version by pushing a tag named `<slug>-v<semver>` (for example, `fabric-buyer-v1.0.0`). The release workflow builds the ZIP and checksum from that tag. A separate reviewed Catalog entry in the registry points to the immutable Release asset and its SHA-256. Creating a Release does not add a plugin to the host's official market automatically.

## Trust and compatibility

The current host MVP accepts only `kind=ai-participation`, `runtime_type=declarative`, API version 1, and the capabilities defined by the host. The host verifies the fixed HTTPS Release URL, exact byte count, SHA-256, manifest, file allowlist, and installation path before atomically installing. Unknown fields, capabilities, runtimes, and resource paths fail closed. `min_host_version` follows PEP 440; plugin `version` follows SemVer.

The initial package directories are source examples only. They are not available in the market until a compatible host adapter is implemented, a Release is reviewed, and a matching Catalog entry is merged.

## License

This repository's tooling, schemas, and official plugin packages are MIT-licensed; see [LICENSE](LICENSE). Each packaged ZIP carries its own copy of the same MIT text, and `scripts/package_plugins.py` verifies that the manifest, the plugin license, and the repository license all stay MIT.

The host application (`pupu-danmu`) is licensed separately and is not relicensed by this repository. Community plugin packages published from other repositories keep whatever license their authors declare.
