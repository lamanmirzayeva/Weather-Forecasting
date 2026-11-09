"""Read-only checks of the saved handoff; never fit or select forecasting models."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def verify_hashes():
    hashes = json.loads((ROOT/'reports/test/reproduction_hashes.json').read_text())
    for name, expected in hashes.items():
        path = ROOT / name.replace('\\', '/')
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
    manifest = json.loads((ROOT/'reports/download_manifest.json').read_text())
    for item in manifest['files']:
        path = ROOT/item['path'].replace('\\', '/')
        # Git checkouts intentionally omit raw inputs; the submission ZIP includes them.
        if path.exists():
            assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], path


def verify_forecasts():
    summary = pd.read_csv(ROOT/'reports/test/test_metrics.csv')
    reference = None
    for model, rows in summary.groupby('model'):
        frame = pd.read_csv(ROOT/f'reports/test/{model}.csv', parse_dates=['origin','target'])
        keys = frame[['origin','target','horizon','actual']]
        if reference is None:
            reference = keys
        else:
            pd.testing.assert_frame_equal(reference, keys)
        assert frame.groupby('horizon').size().to_dict() == {1:366,7:360}
        assert ((frame.target-frame.origin).dt.days == frame.horizon).all()
        for row in rows.itertuples():
            g = frame[frame.horizon.eq(row.horizon)]
            err = g.prediction-g.actual
            np.testing.assert_allclose([np.sqrt(np.mean(err**2)),np.abs(err).mean()],
                                       [row.rmse,row.mae],rtol=1e-12)
            if model != 'persistence':
                np.testing.assert_allclose([
                    ((g.actual>=g.lower)&(g.actual<=g.upper)).mean(),
                    (g.upper-g.lower).mean()], [row.coverage,row.mean_width],rtol=1e-12)


def verify_notebook():
    notebook = json.loads((ROOT/'notebooks/temperature_forecasting_demo.ipynb').read_text(encoding='utf-8'))
    cells = [c for c in notebook['cells'] if c['cell_type']=='code']
    assert len(cells)==10
    assert [c['execution_count'] for c in cells]==list(range(1,11))
    assert not any(o['output_type']=='error' for c in cells for o in c['outputs'])


def verify_powerpoint():
    path = ROOT/'output/presentation/CPTS570_Temperature_Forecasting_Presentation.pptx'
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        slides = [n for n in names if n.startswith('ppt/slides/slide') and n.endswith('.xml') and '/_rels/' not in n]
        notes = [n for n in names if n.startswith('ppt/notesSlides/notesSlide') and n.endswith('.xml') and '/_rels/' not in n]
        charts = [n for n in names if '/charts/chart' in n and n.endswith('.xml')]
        table_count = sum(len(ET.fromstring(archive.read(n)).findall(
            './/{http://schemas.openxmlformats.org/drawingml/2006/main}tbl')) for n in slides)
        assert (len(slides),len(notes),len(charts),table_count)==(12,12,2,3)
        for name in notes:
            text = ''.join(ET.fromstring(archive.read(name)).itertext())
            assert len(text)>100, name


if __name__ == '__main__':
    for check in (verify_hashes,verify_forecasts,verify_notebook,verify_powerpoint):
        check()
        print(check.__name__, 'passed')
    print('Saved handoff checks passed; these checks do not constitute a course submission or human rehearsal.')
