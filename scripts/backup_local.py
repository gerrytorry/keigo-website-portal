"""Offline local backup/restore. Production PostgreSQL uses pg_dump; see docs."""
import argparse,hashlib,json,sqlite3,shutil
from pathlib import Path

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fresh(path):
 if path.exists():raise SystemExit('Destination already exists; choose a NEW directory.')
 path.mkdir(parents=True)
def check_database(path):
 with sqlite3.connect(path) as db:
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise SystemExit('SQLite integrity check failed.')
def backup(source,target):
 db=source/'data.sqlite3'
 if not db.is_file():raise SystemExit('Missing source data.sqlite3.')
 fresh(target)
 with sqlite3.connect(db) as original,sqlite3.connect(target/'data.sqlite3') as destination:original.backup(destination)
 check_database(target/'data.sqlite3')
 media=source/'private-media'
 if media.exists():shutil.copytree(media,target/'private-media')
 files={p.relative_to(target).as_posix():digest(p) for p in target.rglob('*') if p.is_file()}
 (target/'manifest.json').write_text(json.dumps({'format':1,'files':files},indent=2),encoding='utf-8')
 print('Backup verified:',target)
def restore(source,target):
 manifest=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
 for name,expected in manifest['files'].items():
  p=(source/name).resolve()
  if not p.is_relative_to(source.resolve()) or not p.is_file() or digest(p)!=expected:raise SystemExit('Invalid or incomplete backup.')
 check_database(source/'data.sqlite3');fresh(target)
 shutil.copy2(source/'data.sqlite3',target/'data.sqlite3')
 if (source/'private-media').exists():shutil.copytree(source/'private-media',target/'private-media')
 check_database(target/'data.sqlite3');print('Restored to NEW directory:',target)
if __name__=='__main__':
 parser=argparse.ArgumentParser(description='Stop writes/uploads before backup. Never overwrites a restore target.')
 parser.add_argument('action',choices=['backup','restore']);parser.add_argument('source',type=Path);parser.add_argument('target',type=Path)
 args=parser.parse_args();globals()[args.action](args.source.resolve(),args.target.resolve())
