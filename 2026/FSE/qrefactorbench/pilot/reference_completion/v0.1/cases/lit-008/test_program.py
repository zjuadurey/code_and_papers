import json
from pathlib import Path
from copy import deepcopy
import pytest
import kernel
import program


def test_all_byte_pairs_against_bitwise_truth_table():
    for a in range(256):
        for b in range(256):
            bits=''.join('1' if x!=y else '0' for x,y in zip(format(a,'08b'),format(b,'08b')))
            assert kernel.encode(a,b)==(int(bits,2),bits)


def example():return json.loads(Path(__file__).with_name('example_request.json').read_text())


def test_three_original_humaneval_examples():
    r=example();before=deepcopy(r);out=program.review(r)
    assert [x['counts'] for x in out['receipts']]==[{'00011110':1024},{'00110100':1024},{'00100111':1024}]
    assert [x['prefix_checksum'] for x in out['receipts']]==[30,82,121]
    assert out['checksum']==121 and r==before


def test_repeats_inspect_empty_and_order():
    r=example();r.update(mode='inspect',repetitions=9)
    assert all(x['counts'] is None for x in program.review(r)['receipts'])
    r['records'].reverse();assert program.review(r)['receipts'][0]['id']=='r2'
    r['records']=[];assert program.review(r)=={'record_count':0,'receipts':[],'checksum':0}


def test_wrong_endian_does_not_preserve_output(monkeypatch):
    original=kernel.encode
    monkeypatch.setattr(program,'encode',lambda a,b:(original(a,b)[0],original(a,b)[1][::-1]))
    assert program.review(example())['receipts'][0]['counts']!={'00011110':1024}


@pytest.mark.parametrize('value',[-1,256,True,1.2])
def test_invalid_byte(value):
    r=example();r['records'][-1]['left']=value
    with pytest.raises(ValueError):program.review(r)


def test_validate_late_record_before_processing(monkeypatch):
    r=example();r['records'][-1]['id']='r0'
    monkeypatch.setattr(program,'encode',lambda *_:pytest.fail('full validation first'))
    with pytest.raises(ValueError):program.review(r)
