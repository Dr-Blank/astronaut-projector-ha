#!/usr/bin/env bash
# Link the integration into the Home Assistant devcontainer's config directory.
#
# Requires the devcontainer to bind mount this repository at
# /workspaces/astronaut-projector-ha, so the symlink resolves inside the container. Edits on
# the host are then live; Home Assistant still needs a restart to pick up
# changed Python.
set -euo pipefail

DEST="${HA_CORE:-$HOME/projects/ha-core}/config/custom_components"

mkdir -p "$DEST"
rm -rf "${DEST:?}/astronaut_projector_infrared"
ln -s /workspaces/astronaut-projector-ha/custom_components/astronaut_projector_infrared "$DEST/astronaut_projector_infrared"
echo "linked $DEST/astronaut_projector_infrared -> /workspaces/astronaut-projector-ha/custom_components/astronaut_projector_infrared"
