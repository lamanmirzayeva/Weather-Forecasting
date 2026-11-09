"""Package selected project files and cached data without local tools or secrets."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'output/submission'
FINAL = OUT/'CPTS570_Submission_Package.zip'


def selected_files():
    selected = [ROOT/n for n in ['README.md','SUBMISSION_README.md','requirements.txt','.gitignore','.gitattributes']]
    extensions = {
        'scripts': {'.py'}, 'notebooks': {'.ipynb','.md'},
        'reports': {'.csv','.json','.md','.txt','.png'},
        'paper': {'.tex','.sty','.pdf','.md'},
        'presentation': {'.mjs','.md'}, 'data': {'.csv','.txt'},
    }
    for folder, suffixes in extensions.items():
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and p.suffix in suffixes and '__pycache__' not in p.parts:
                if p in [ROOT/'paper/main.pdf',ROOT/'paper/neurips_2026.sty',ROOT/'reports/notebook_preview.png']:
                    continue
                selected.append(p)
    selected = [p for p in selected if p.name != 'github_payload.py']
    selected.extend([ROOT/'output/pdf/CPTS570_Temperature_Forecasting_Academic_Revision.pdf',
                     ROOT/'output/presentation/CPTS570_Temperature_Forecasting_Presentation.pptx'])
    return sorted(set(selected),key=lambda p:p.relative_to(ROOT).as_posix())


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    files = selected_files()
    manifest = []
    with zipfile.ZipFile(FINAL,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in files:
            name = path.relative_to(ROOT).as_posix()
            assert not path.is_symlink()
            archive.write(path,name)
            manifest.append(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+name)
        archive.writestr('MANIFEST.sha256','\n'.join(manifest)+'\n')
    # Verify archive CRCs and every payload digest without trusting the source tree.
    with zipfile.ZipFile(FINAL) as archive:
        assert archive.testzip() is None
        for line in archive.read('MANIFEST.sha256').decode().splitlines():
            digest,name = line.split('  ',1)
            assert hashlib.sha256(archive.read(name)).hexdigest()==digest,name
        assert len(archive.namelist())==len(files)+1
    print(f'Packaged and verified {len(files)} files: {FINAL}')
    print(f'ZIP size: {FINAL.stat().st_size/1024/1024:.2f} MiB')


if __name__=='__main__':
    main()
