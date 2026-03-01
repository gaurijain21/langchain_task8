# chains/prove_chain.py
from langchain_core.runnables import RunnableLambda
from tools.bc_tool import prove_with_bc

def build_chain():
    return RunnableLambda(lambda query: prove_with_bc(query))