"""Execute every notebook cell with a project-local kernel and save outputs."""
import json
import os
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[1]
kernel_root = ROOT/'.venv/share/jupyter/kernels'
kernel = kernel_root/'project-demo'
kernel.mkdir(parents=True, exist_ok=True)
(kernel/'kernel.json').write_text(json.dumps({
    'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
    'display_name':'Project demo','language':'python'}))
runtime = ROOT/'.venv/jupyter-runtime'
runtime.mkdir(parents=True, exist_ok=True)
os.environ['JUPYTER_RUNTIME_DIR'] = str(runtime)
os.environ['IPYTHONDIR'] = str(ROOT/'.venv/ipython')
path = ROOT/'notebooks/temperature_forecasting_demo.ipynb'
nb = nbformat.read(path, as_version=4)
nbformat.validate(nb)
manager = KernelManager(kernel_name='project-demo',
    kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernel_root)]))
NotebookClient(nb, km=manager, timeout=300, resources={'metadata':{'path':str(ROOT)}}).execute(cwd=str(ROOT))
nbformat.validate(nb)
nbformat.write(nb,path)
counts = [c.execution_count for c in nb.cells if c.cell_type=='code']
assert counts == list(range(1,len(counts)+1)), counts
assert not any(o.output_type=='error' for c in nb.cells if c.cell_type=='code' for o in c.outputs)
print(f'Executed and validated {len(counts)} code cells; outputs saved to {path}')
