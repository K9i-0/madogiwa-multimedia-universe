"""Reuse phrase-safe caption timing with v5 terms and output paths."""
import sys
import prepare_captions_v2 as captions
captions.TERMS += ['Unity', 'Flutter']
captions.READINGS.update({'Unity':'ユニティ', 'Flutter':'フラッター'})
if '--input' not in sys.argv: sys.argv += ['--input','src/edit-manifest-v5.json']
if '--plan' not in sys.argv: sys.argv += ['--plan','captions-plan-v5.json']
captions.main()
