import math
import sys
import pytest
from methods import backward_error,distribution_report,objective_report,pass_at_k,symmetry_defect


def test_pass_at_k_hand_fixture():
    assert pass_at_k(4,1,2)==0.5
    assert pass_at_k(4,2,2)==pytest.approx(5/6)
    assert pass_at_k(4,0,2)==0 and pass_at_k(4,4,1)==1


@pytest.mark.parametrize('args',[(1,1,2),(0,0,1),(4,5,1),(4,1,0),(True,0,1)])
def test_invalid_sampling_denominators(args):
    with pytest.raises(ValueError):pass_at_k(*args)


def test_distribution_direction_zero_mass_and_no_threshold():
    same=distribution_report({'00':1,'11':1},{'00':500,'11':500})
    assert same['total_variation']==0 and same['hellinger_fidelity']==pytest.approx(1)
    missing=distribution_report({'00':1,'11':1},{'00':1})
    assert missing['kl_is_infinite'] and missing['kl_reference_to_observed'] is None
    reverse=distribution_report({'00':1},{'00':1,'11':1})
    assert reverse['kl_reference_to_observed']==pytest.approx(math.log(2))
    assert same['acceptance'] is None


@pytest.mark.parametrize('values',[{}, {'0':0}, {'0':-1},{'0':float('nan')},{'0':True}])
def test_invalid_distributions(values):
    with pytest.raises(ValueError):distribution_report(values,{'0':1})


def test_same_objective_can_hide_distribution_change():
    p,q={'00':1},{'11':1};values={'00':2,'11':2}
    assert objective_report(p,q,values)['absolute_expectation_gap']==0
    assert distribution_report(p,q)['total_variation']==1
    assert objective_report({'0':1},{'1':1},{'0':0,'1':-3})['absolute_expectation_gap']==3


def test_numerical_checks_detect_wrong_result_without_acceptance_policy():
    a=[[4,1],[1,3]];b=[1,2]
    good=backward_error(a,b,[1/11,7/11],sys.float_info.epsilon)
    bad=backward_error(a,b,[0,0],sys.float_info.epsilon)
    assert good['residual_infinity_norm']<1e-14 and bad['residual_infinity_norm']==2
    assert good['acceptance'] is None
    assert symmetry_defect(a,[1,0],[0,1])==0
    assert symmetry_defect([[4,2],[1,3]],[1,0],[0,1])==1
