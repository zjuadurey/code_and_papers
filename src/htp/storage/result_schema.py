import json

def parse_native(text):
    r=json.loads(text)
    if r.get('status')!='PASS': raise ValueError('Native run did not pass')
    for key in ['algorithmic_read_bytes','algorithmic_write_bytes','total_elapsed_s','peak_rss_bytes']:
        if key not in r or r[key]<0: raise ValueError(f'Invalid {key}')
    b=r['old_state_bytes']
    expected={'NAIVE_PRODUCT':(3*b,4*b),'NAIVE_BASIS':(3*b,4*b),
              'THIN_BASIS':(3*b,3*b),'PRODUCT_FUSED':(b,2*b),'FUSED_BASIS':(b,2*b)}
    if (r['algorithmic_read_bytes'],r['algorithmic_write_bytes'])!=expected[r['policy']]:
        raise ValueError('Algorithmic traffic does not match implemented passes')
    if r['logical_output_bytes']!=2*b: raise ValueError('Output size incorrect')
    return r
