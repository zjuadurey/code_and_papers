import ast
import logging
import random
from pathlib import Path
import pytest
from htp.qdao_model import partition

def test_partition_against_original_source():
    path=Path(__file__).resolve().parents[1]/'external/qdao/qdao/circuit.py'
    tree=ast.parse(path.read_text())
    cls=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=='StaticPartitioner')
    class Base:
        pass
    namespace={'BasePartitioner':Base,'Any':object,'List':list,'QdaoCircuit':object,'logging':logging}
    exec(compile(ast.Module(body=[cls],type_ignores=[]),str(path),'exec'),namespace)
    class Wrapper:
        instructions=[]
        def get_instr_qubits(self,inst): return inst[1]
        def gen_sub_circ(self,instrs,t,m):
            class Sub:
                circ='stub'
            sub=Sub(); sub.indices=[i[0] for i in instrs]; return sub
    rng=random.Random(72)
    for _ in range(100):
        ops=[rng.sample(range(25),rng.randrange(1,4)) for _ in range(80)]
        obj=namespace['StaticPartitioner'](); obj._np=8; obj._nl=2; obj._circ_helper=Wrapper()
        obj._circ_helper.instructions=list(enumerate(ops))
        expected=[(s.indices[0],s.indices[-1]+1) for s in obj.run(None)]
        assert partition(ops,8,2)==expected

def test_oversized_instruction():
    with pytest.raises(ValueError): partition([list(range(10))],4,2)
