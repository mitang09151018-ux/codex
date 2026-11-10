#!/usr/bin/env python3
"""Synthesize authorized user text with a saved ElevenLabs voice profile."""
import argparse
import base64
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--text-file', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--timestamps', action='store_true')
    parser.add_argument('--check', action='store_true', help='Validate profile locally; no API request')
    args = parser.parse_args()
    profile_file = Path(__file__).resolve().parents[1] / 'references/voice-profile.json'
    profile = json.loads(profile_file.read_text(encoding='utf-8'))
    for field in ('voice_id', 'model_id', 'voice_settings', 'api_key_env', 'output_format'):
        if not profile.get(field):
            parser.error('Voice profile is missing ' + field)
    if args.check:
        print(json.dumps({'profile_valid': True, 'voice_name': profile['name'],
                          'model': profile['model_id'], 'api_key_configured': bool(os.environ.get(profile['api_key_env']))}, ensure_ascii=False))
        return 0
    if not args.text_file or not args.output:
        parser.error('--text-file and --output are required for synthesis')
    if args.output.suffix.lower() != '.mp3':
        parser.error('--output must end in .mp3')
    meta = args.output.with_suffix('.alignment.json')
    if args.output.exists() or (args.timestamps and meta.exists()):
        parser.error('Output already exists; choose a new filename')
    text = args.text_file.read_text(encoding='utf-8')
    if not text.strip():
        parser.error('The script is empty')
    key = os.environ.get(profile['api_key_env'], '').strip()
    if not key:
        parser.error('Set ' + profile['api_key_env'] + ' in the local environment; do not paste it into chat')
    endpoint = 'https://api.elevenlabs.io/v1/text-to-speech/' + urllib.parse.quote(profile['voice_id'], safe='')
    if args.timestamps:
        endpoint += '/with-timestamps'
    endpoint += '?' + urllib.parse.urlencode({'output_format': profile['output_format']})
    payload = {k: profile[k] for k in ('model_id', 'voice_settings')}
    payload['text'] = text
    request = urllib.request.Request(endpoint, data=json.dumps(payload).encode('utf-8'),
                                     headers={'xi-api-key': key, 'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = response.read()
    except urllib.error.HTTPError as error:
        print('ElevenLabs returned HTTP ' + str(error.code) + '. No automatic retry.', file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError, OSError):
        print('Request failed; generation outcome may be unknown. Check ElevenLabs history before retrying.', file=sys.stderr)
        return 1
    alignment = None
    if args.timestamps:
        try:
            decoded = json.loads(data)
            audio = base64.b64decode(decoded.pop('audio_base64'), validate=True)
            alignment = decoded
        except (ValueError, KeyError, TypeError):
            print('Unexpected audio response. No automatic retry.', file=sys.stderr)
            return 1
    else:
        audio = data
    if len(audio) < 4 or not (audio.startswith(b'ID3') or (audio[0] == 255 and audio[1] & 224 == 224)):
        print('Response is not recognizable MP3. No automatic retry.', file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as output:
        output.write(audio)
    if alignment is not None:
        with meta.open('x', encoding='utf-8') as output:
            json.dump(alignment, output, ensure_ascii=False, indent=2)
    print(json.dumps({'audio': str(args.output), 'alignment': str(meta) if alignment else None, 'bytes': len(audio)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
