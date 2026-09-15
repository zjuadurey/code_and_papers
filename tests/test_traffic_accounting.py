import pytest
from htp.materialization_policy import ImplicitZeroExpansion, materialization_cost
from htp.traffic_model import compose_traffic, rounded_bytes


def test_known_one_branch_reuses_old_extent():
    e=ImplicitZeroExpansion(1024,(1,0,1))
    assert e.active_branch==5 and e.physical_bytes_at_insertion==1024
    assert e.logical_bytes==8192 and e.branch(5)=='EXISTING' and e.branch(0)=='ZERO'


def test_thin_first_h_output_not_free():
    c=materialization_cost('BASIS_THIN',3,1)
    assert c['insertion_write_bytes']==0 and c['write_bytes']==256 and c['read_bytes']==128


def test_hand_traffic_and_boundary_credit():
    event=dict(gate_index=1,old_q=0,new_q=2,materialization_batch_size=2)
    r=compose_traffic([0,2],[event],[(0,1)],'PRODUCT_FUSED')
    assert r['predicted_qdao_bytes']==80 and r['predicted_materialization_bytes']==80
    assert r['predicted_total_bytes']==160 and r['predicted_total_boundary_fused']==80
    b=compose_traffic([0,2],[event],[(0,1)],'BASIS_REWRITE')
    assert b['predicted_total_boundary_fused']==160


def test_complex_precision_scaling():
    e=[dict(gate_index=1,old_q=0,materialization_batch_size=2)]
    a=compose_traffic([0,2],e,[(0,1)],'PRODUCT_FUSED',8)
    b=compose_traffic([0,2],e,[(0,1)],'PRODUCT_FUSED',16)
    assert b['predicted_total_bytes']==2*a['predicted_total_bytes']


def test_chunk_roundup():
    assert rounded_bytes(16,4096)==4096 and rounded_bytes(0,4096)==0
    assert rounded_bytes(4097,4096)==8192
