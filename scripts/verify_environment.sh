#!/usr/bin/env bash
# ============================================================================
# HYDAT-X — verify_environment.sh  (test de santé global)
# Vérifie outils, dépendances Python, données HYDAT, schéma, inventaire,
# manifeste et provenance. Sortie PAS/FAIL structurée ; exit code non nul si
# un élément critique échoue.
# ============================================================================
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

declare -A RESULTS=()
declare -A NOTES=()

check() { # name command...
  local name="$1"; shift
  if "$@" > /dev/null 2>&1; then RESULTS["$name"]="PASS"; else RESULTS["$name"]="FAIL"; fi
}

check_soft() { # name command...
  local name="$1"; shift
  if "$@" > /dev/null 2>&1; then RESULTS["$name"]="PASS"; else RESULTS["$name"]="FAIL"; NOTES["$name"]="non-critique, attesté dans metadata/provenance/soup-environment.txt"; fi
}

for tool in git nix python uv sqlite3 duckdb curl unzip jq soup; do
  check "tool:$tool" command -v "$tool"
  NOTES["tool:$tool"]="$(command -v "$tool" 2>/dev/null || echo 'commande absente')"
done

# Dépendances Python (venv projet s'il existe, sinon interpréteur courant)
PY="python"
[ -x "$ROOT/.venv/bin/python" ] && PY="$ROOT/.venv/bin/python"
NOTE_PY="python = $PY ($("$PY" --version 2>&1))"
check "python:imports" "$PY" -c "import pandas, numpy, scipy, sklearn, duckdb"
NOTES["python:imports"]="$NOTE_PY"

# Base HYDAT présente (détection dans data/raw/hydat/<release>/)
DB_FILE="$(find data/raw/hydat -maxdepth 3 -type f \( -name '*.sqlite' -o -name '*.sqlite3' -o -name '*.db' \) 2>/dev/null | head -n1 || true)"
if [ -n "$DB_FILE" ]; then
  RESULTS["hydat:db"]="PASS"; NOTES["hydat:db"]="$DB_FILE"
else
  RESULTS["hydat:db"]="FAIL"; NOTES["hydat:db"]="aucune base HYDAT dans data/raw/hydat/"
fi

# Inspection + inventaire déjà produits ?
if [ -f metadata/stations/hydat-schema.json ] && [ -f metadata/stations/hydat-schema.txt ]; then
  RESULTS["hydat:schema"]="PASS"; NOTES["hydat:schema"]="metadata/stations/hydat-schema.{json,txt}"
else
  RESULTS["hydat:schema"]="FAIL"; NOTES["hydat:schema"]="manquants"
fi
if [ -f metadata/stations/station-inventory.parquet ]; then
  RESULTS["hydat:inventory"]="PASS"; NOTES["hydat:inventory"]="metadata/stations/station-inventory.parquet"
else
  RESULTS["hydat:inventory"]="FAIL"; NOTES["hydat:inventory"]="manquant"
fi

MANIFEST="$(find registry/datasets -name 'hydat-reference-*.yaml' 2>/dev/null | sort | tail -n1 || true)"
if [ -n "$MANIFEST" ]; then
  RESULTS["dataset:manifest"]="PASS"; NOTES["dataset:manifest"]="$MANIFEST"
else
  RESULTS["dataset:manifest"]="FAIL"; NOTES["dataset:manifest"]="manquant"
fi

PROV="$(find metadata/downloads -name 'hydat-*-download-manifest.yaml' 2>/dev/null | sort | tail -n1 || true)"
if [ -n "$PROV" ]; then
  RESULTS["provenance"]="PASS"; NOTES["provenance"]="$PROV"
else
  RESULTS["provenance"]="FAIL"; NOTES["provenance"]="manquant"
fi

# ---------------------------------------------------------------------------
echo "========================================"
echo "HYDAT-X ENVIRONMENT CHECK"
echo "========================================"
for k in $(printf '%s\n' "${!RESULTS[@]}" | sort); do
  printf '[%s] %s   (%s)\n' "${RESULTS[$k]}" "$k" "${NOTES[$k]:-}"
done
echo "========================================"

# Verdicts agrégés
env_pass() {
  local all=1 k
  for k in "${!RESULTS[@]}"; do case "$k" in tool:*|python:imports) [ "${RESULTS[$k]}" = "PASS" ] || all=0;; esac; done
  [ "$all" = "1" ] && echo "PASS" || echo "FAIL"
}

echo "HYDAT-X ENVIRONMENT: $(env_pass)"
echo "HYDAT REFERENCE: ${RESULTS[hydat:db]}"
echo "SOUP CLI: ${RESULTS[tool:soup]}"
echo "SQLITE INSPECTION: ${RESULTS[hydat:schema]}"
echo "STATION INVENTORY: ${RESULTS[hydat:inventory]}"
echo "PROVENANCE: ${RESULTS[provenance]}  (+ dataset:manifest ${RESULTS[dataset:manifest]})"
echo "========================================"

FAILED=""
for k in "${!RESULTS[@]}"; do
  [ "${RESULTS[$k]}" = "FAIL" ] && FAILED="$FAILED $k"
done

if [ -n "$FAILED" ]; then
  echo "ÉCHEC critique sur :$FAILED"
  exit 1
fi
exit 0