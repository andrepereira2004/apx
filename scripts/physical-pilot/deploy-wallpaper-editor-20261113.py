#!/usr/bin/env python3
"""Deploy the bounded wallpaper editor update on the fixed physical pilot."""
import importlib.util
from pathlib import Path

source = Path(__file__).with_name('deploy-keyboard-controls-20261111.py')
spec = importlib.util.spec_from_file_location('apx_bounded_asset_deploy', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.ASSETS = (
    'local/bin/apx-lock-wallpaper-v1',
    'local/bin/apx-appearance-v1',
    'quickshell/apx/Appearance.qml',
    'quickshell/apx/PersonalizationPanel.qml',
    'quickshell/apx/WorkspacePreview.qml',
    'quickshell/apx/shell.qml',
)
module.main()
