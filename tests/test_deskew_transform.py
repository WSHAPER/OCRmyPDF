# SPDX-FileCopyrightText: 2026 WSHAPER
# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

import json

import pytest

from ocrmypdf.exceptions import BadArgsError

from .conftest import check_ocrmypdf, run_ocrmypdf_api


def test_deskew_transform(resources, outdir):
    # Default filename: the sidecar lands next to the output file
    check_ocrmypdf(
        resources / 'skew.pdf',
        outdir / 'skew.pdf',
        '--deskew',
        '--deskew-transform',
    )
    sidecar = outdir / 'skew.pdf.deskew.json'
    assert sidecar.exists()
    data = json.loads(sidecar.read_text(encoding='utf-8'))
    assert data['version'] == 1
    assert len(data['pages']) == 1
    page = data['pages'][0]
    assert page['page'] == 1
    # skew.pdf has a real, measurable skew
    assert abs(page['angle_deg']) > 0.1
    assert len(page['image_size']) == 2 and all(size > 0 for size in page['image_size'])
    assert len(page['dpi']) == 2 and all(dpi > 0 for dpi in page['dpi'])
    assert page['expand'] is False
    assert page['resample'] == 'bicubic'
    assert page['fill'] == 'white'
    # rotation is about the image center
    assert page['center'] == [page['image_size'][0] / 2, page['image_size'][1] / 2]


def test_deskew_transform_explicit_filename(resources, outdir):
    check_ocrmypdf(
        resources / 'skew.pdf',
        outdir / 'skew.pdf',
        '--deskew',
        '--deskew-transform',
        str(outdir / 'transform.json'),
    )
    assert (outdir / 'transform.json').exists()
    assert (
        json.loads((outdir / 'transform.json').read_text(encoding='utf-8'))['pages'][0][
            'angle_deg'
        ]
        != 0.0
    )


def test_deskew_transform_requires_deskew(resources, no_outpdf):
    with pytest.raises(BadArgsError, match=r'--deskew'):
        run_ocrmypdf_api(resources / 'skew.pdf', no_outpdf, '--deskew-transform')


def test_deskew_transform_rejects_input_file(resources, outdir):
    with pytest.raises(BadArgsError, match=r'--deskew-transform'):
        run_ocrmypdf_api(
            resources / 'skew.pdf',
            outdir / 'skew.pdf',
            '--deskew',
            '--deskew-transform',
            str(resources / 'skew.pdf'),
        )
