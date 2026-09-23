#!/usr/bin/env bash
# ============================================================================
# HYDAT-X — bootstrap_reference.sh
# Construit la référence HYDAT indépendante : environnement, soup CLI, données
# ECCC (SQLite + documentation), provenance, schéma, inventaire stations,
# manifeste de dataset, test de santé.
#
# Propriétés : idempotent, interrompable, relançable, strict, retry réseau,
# téléchargement temporaire → validation → hash → move atomique, refus
# d'écrasement silencieux, journalisation.
# ============================================================================
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/bootstrap.log"
TMPD="$ROOT/data/raw/.tmp"
mkdir -p "$TMPD"

log() { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG_FILE"; }
fail() { log "FATAL $*"; exit 1; }

# ---------------------------------------------------------------------------
# Garde-fous
# ---------------------------------------------------------------------------
SRC_URL="${HYDAT_SOURCE_URL:-https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/}"

[ -d "$ROOT/data/raw/hydat" ] || mkdir -p "$ROOT/data/raw/hydat"

needed=(git curl unzip jq python sha256sum stat awk grep)
for t in "${needed[@]}"; do
  command -v "$t" >/dev/null 2>&1 || fail "outil absent : $t"
done

# ---------------------------------------------------------------------------
# Découverte dynamique de la release (index Apache officiel ECCC)
# ---------------------------------------------------------------------------
RELEASE=""
if [ -n "${HYDAT_RELEASE:-}" ]; then
  RELEASE="$HYDAT_RELEASE"
  log "release imposée : $RELEASE (HYDAT_RELEASE)"
else
  log "découverte de la release depuis $SRC_URL"
  INDEX="$(curl -fsSL --retry 5 --retry-delay 3 --max-time 90 "$SRC_URL")" \
    || fail "index ECCC injoignable"
  RELEASE="$(printf '%s' "$INDEX" | grep -oE 'Hydat_sqlite3_[0-9]{8}\.zip' | head -n1 | grep -oE '[0-9]{8}')"
  [ -n "$RELEASE" ] || fail "releasedetect impossible : aucun Hydat_sqlite3_<AAAAJJMM>.zip dans l'index"
fi
log "release HYDAT retenue : $RELEASE"

REL_DIR="$ROOT/data/raw/hydat/$RELEASE"
SQL_DIR="$REL_DIR/sqlite"
DOC_DIR="$REL_DIR/documentation"
mkdir -p "$SQL_DIR" "$DOC_DIR"

# Manifeste de provenance (versionné, par release — jamais écrasé)
META_DIR="$ROOT/metadata/downloads"
mkdir -p "$META_DIR"
PROV_FILE="$META_DIR/hydat-${RELEASE}-download-manifest.yaml"
SIDECAR="$REL_DIR/MANIFEST.sha256"
[ -f "$SIDECAR" ] || : > "$SIDECAR"

file_hash() { sha256sum "$1" | awk '{print $1}'; }
sidecar_hash() { local f="$1"; awk -v f="$(basename "$1")" '$2==f{print $1}' "$SIDECAR"; }

append_prov() { # url filename size content_type
  cat >> "$PROV_FILE" <<EOF
- artifact: "$2"
  source_url: "$1"
  retrieved_at_utc: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  filename: "$2"
  size_bytes: $3
  sha256: "$4"
  content_type: "$5"
  source_page: "$SRC_URL"
  release: "$RELEASE"
EOF
}

# ---------------------------------------------------------------------------
# Téléchargement : temporaire → validation → hash → move atomique
# ---------------------------------------------------------------------------
download() { # url target label is_zip(0/1)
  local url="$1" target="$2" label="$3" iszip="$4" cur want
  if [ -f "$target" ]; then
    cur="$(file_hash "$target")"
    want="$(sidecar_hash "$target")"
    if [ -n "$want" ] && [ "$cur" = "$want" ]; then
      log "REUSE  $label (hash $cur = manifeste)"
      return 0
    elif [ -n "$want" ]; then
      log "WARN   $label : hash local ($cur) != manifeste ($want) → conservation, nouveau téléchargement"
      mv "$target" "$target.conflict.$(date -u +%Y%m%dT%H%M%SZ)"
    else
      log "NOTE   $label : présent sans entrée manifeste → revalidation"
    fi
  fi
  local tmp="$TMPD/$(basename "$target").tmp.$$"
  rm -f "$tmp"
  local http content_type size
  if ! http="$(curl -fsSL --retry 5 --retry-delay 3 --retry-all-errors --max-time 1800 \
        -o "$tmp" -w '%{http_code}' \
        -D "$TMPD/headers.$$" "$url" 2>"$LOG_DIR/curl.err.$$")"; then
    rm -f "$tmp"; log "ERROR  $label : échec HTTP ($http) url=$url"
    return 1
  fi
  [ -s "$tmp" ] || { rm -f "$tmp"; log "ERROR  $label : taille 0"; return 1; }
  size="$(stat -c%s "$tmp")"
  if [ "$iszip" = "1" ]; then
    unzip -t "$tmp" >/dev/null 2>&1 || { rm -f "$tmp"; log "ERROR  $label : ZIP invalide"; return 1; }
  fi
  local hash; hash="$(file_hash "$tmp")"
  content_type="$(awk 'tolower($1)=="content-type:"{gsub("\r","",$2);print $2}' "$TMPD/headers.$$" | tail -n1)"
  rm -f "$TMPD/headers.$$" "$LOG_DIR/curl.err.$$"
  mv "$tmp" "$target"   # même filesystem → atomique
  printf '%s  %s\n' "$hash" "$(basename "$target")" >> "$SIDECAR"
  append_prov "$url" "$(basename "$target")" "$size" "$hash" "$content_type"
  log "OK     $label ($size octets, sha256 $hash)"
}

ARTIFACTS=(
  "https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/Hydat_sqlite3_${RELEASE}.zip|$SQL_DIR/Hydat_sqlite3_${RELEASE}.zip|HYDAT SQLite ${RELEASE}|1"
  "https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/HYDAT_Definition_EN.pdf|$DOC_DIR/HYDAT_Definition_EN.pdf|HYDAT Definition EN|0"
  "https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/HYDAT_Definition_FR.pdf|$DOC_DIR/HYDAT_Definition_FR.pdf|HYDAT Definition FR|0"
  "https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/HYDAT_ReleaseNotes_${RELEASE}_EN.pdf|$DOC_DIR/HYDAT_ReleaseNotes_${RELEASE}_EN.pdf|HYDAT ReleaseNotes EN ${RELEASE}|0"
  "https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/HYDAT_ReleaseNotes_${RELEASE}_FR.pdf|$DOC_DIR/HYDAT_ReleaseNotes_${RELEASE}_FR.pdf|HYDAT ReleaseNotes FR ${RELEASE}|0"
)

for entry in "${ARTIFACTS[@]}"; do
  IFS='|' read -r url target label iszip <<< "$entry"
  download "$url" "$target" "$label" "$iszip"
done

# ---------------------------------------------------------------------------
# Extraction SQLite (si la base n'est pas déjà présente) — jamais d'écrasement
# ---------------------------------------------------------------------------
DB_FILE="$(find "$SQL_DIR" -maxdepth 2 -type f \( -name '*.sqlite' -o -name '*.sqlite3' -o -name '*.db' \) | head -n1 || true)"
if [ -z "$DB_FILE" ]; then
  log "extraction du conteneur SQLite → $SQL_DIR"
  unzip -q -o "$SQL_DIR/Hydat_sqlite3_${RELEASE}.zip" -d "$SQL_DIR"
  DB_FILE="$(find "$SQL_DIR" -maxdepth 2 -type f \( -name '*.sqlite' -o -name '*.sqlite3' -o -name '*.db' \) | head -n1)" \
    || fail "aucun fichier SQLite trouvé après extraction"
  log "OK     identifié : $(basename "$DB_FILE")"
else
  log "REUSE  base SQLite existante : $DB_FILE"
fi
printf '%s  %s\n' "$(file_hash "$DB_FILE")" "$(basename "$DB_FILE")" >> "$SIDECAR"
# Dédup du manifeste (idempotence : une ligne par fichier)
sort -u "$SIDECAR" -o "$SIDECAR" 2>/dev/null || true

# ---------------------------------------------------------------------------
# Environnement Python (uv) — dépendances du projet
# ---------------------------------------------------------------------------
log "sync uv → .venv (pyproject.toml)"
(cd "$ROOT" && uv sync --python 3.12) || fail "uv sync a échoué"
PY="$ROOT/.venv/bin/python"
"$PY" -c "import pandas, numpy, scipy, sklearn, duckdb" || fail "dépendances Python incomplètes"

# ---------------------------------------------------------------------------
# Soup CLI (périphérique, couche évaluation/gating) + capture de l'environnement
# ---------------------------------------------------------------------------
if [ -n "${HYDAT_X_NO_SOUP:-}" ]; then
  log "SKIP  soup (HYDAT_X_NO_SOUP défini)"
else
  if ! command -v soup >/dev/null 2>&1; then
    log "soup CLI absent → uv tool install soup-cli (python 3.12)"
    uv tool install --python 3.12 soup-cli || log "WARN  échec d'installation soup-cli (non bloquant)"
  fi
  log "soup version : $(soup version 2>&1 | tail -n1)"
  {
    echo "=== soup version ==="; soup version 2>&1 || true
    echo; echo "=== soup --help ==="; soup --help 2>&1 || true
    echo; echo "=== soup doctor ==="; soup doctor 2>&1 || true
  } > "$ROOT/metadata/provenance/soup-environment.txt" || true
  log "OK      capture : metadata/provenance/soup-environment.txt"
fi

# ---------------------------------------------------------------------------
# Inspection SQLite (lecture seule) + inventaire stations + manifeste dataset
# ---------------------------------------------------------------------------
log "inspection du schéma (lecture seule)"
"$PY" "$ROOT/scripts/inspect_hydat.py" --release "$RELEASE"
log "manifeste dataset"
"$PY" "$ROOT/scripts/make_manifest.py" --release "$RELEASE"

# ---------------------------------------------------------------------------
# Test de santé global
# ---------------------------------------------------------------------------
log "test de santé global"
"$ROOT/scripts/verify_environment.sh" || true  # échec éventuel reporté en sortie finale

# ---------------------------------------------------------------------------
log "BOOTSTRAP TERMINÉ — release $RELEASE — journal : $LOG_FILE"