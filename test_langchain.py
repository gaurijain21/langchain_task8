from chains.prove_chain import build_chain

if __name__ == "__main__":
    chain = build_chain()

    out = chain.invoke("ancestor(john, sue)")
    print("Query:", out["query"])
    print("Parsed:", out["parsed_query"])
    print("Result:", out["result"])
    print("RAG used rules:", out["rag_used_rules"])
    print("Trace:")
    for t in out["trace"]:
        print("-", t)