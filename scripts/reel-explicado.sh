#!/usr/bin/env bash
# Arma un reel "Lo que te diría tu contador" de punta a punta: voz → música a medida → mezcla → video.
# Uso: bash scripts/reel-explicado.sh <reel.json> <salida.mp4>
# La voz sale de ElevenLabs (ELEVENLABS_API_KEY y ELEVENLABS_VOICE_ID); si falla o no hay clave, usa la voz gratis
# es-AR-TomasNeural (edge-tts) para que el reel salga igual. Los archivos intermedios quedan junto a la salida.
set -euo pipefail
PY="${PYTHON:-python3}"   # en Windows: PYTHON=python bash scripts/reel-explicado.sh ...
reel="$1"; out="$2"
dir="$(dirname "$out")/$(basename "$out" .mp4)-armado"
mkdir -p "$dir"

if ! "$PY" scripts/voz-reel.py "$reel" "$dir" eleven; then
  echo "ElevenLabs no respondió: uso la voz de respaldo (edge-tts)"
  echo "edge-tts" > "$dir/voz-respaldo.txt"
  "$PY" scripts/voz-reel.py "$reel" "$dir" es-AR-TomasNeural
fi
"$PY" scripts/audio-explicado.py "$dir/musica.wav" "$dir/datos.json"
# La música baja sola cuando habla la voz (sidechain) y después se suman las dos.
ffmpeg -v error -y -i "$dir/musica.wav" -i "$dir/voz.wav" -filter_complex \
  "[1]aformat=channel_layouts=stereo,asplit[v1][v2];[0][v1]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350[m];[m][v2]amix=inputs=2:weights='0.7 1':normalize=0,alimiter=limit=0.95" \
  "$dir/mezcla.wav"
total="$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1],encoding='utf-8'))['total'])" "$dir/datos.json")"
node scripts/render-animada.mjs --datos "$dir/datos.json" templates/reel-explicado.html "$out" "$total" 30 "$dir/mezcla.wav"
