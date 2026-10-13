# Pupu Danmu plugin migration source

This repository is retained as the historical source and migration reference for the official data-only plugins. It is no longer the official development or Release target. Future changes belong in the individual official repositories:

- [fabric-buyer](https://github.com/pupujiang-org/pupu-danmu-plugin-fabric-buyer)
- [music-audience](https://github.com/pupujiang-org/pupu-danmu-plugin-music-audience)

Each plugin repository owns its Manifest, source resources, MIT license, validation, CI, version tag, and Release workflow. The ZIP and SHA-256 assets are generated from that repository's tag and uploaded to its GitHub Release. They must not be committed here or in the individual plugin repositories.

The [plugin registry](https://github.com/pupujiang-org/pupu-danmu-plugin-registry) stores reviewed Catalog metadata and the generated index; it does not store plugin source or packages. The host accepts official Releases only from the repository mapped to each official plugin ID.

The source here predates the split and remains useful when tracing the migration. Do not publish new official plugin versions from this repository. It will remain available until its history and any remaining references have been reviewed before archival.
