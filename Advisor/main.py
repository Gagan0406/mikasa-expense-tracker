from graph import build_graph

if __name__ == "__main__":
    app = build_graph()

    user_query = input("\n🧑 Enter your query: ")

    result = app.invoke({
        "user_query": user_query
    })

    print("\n✅ FINAL OUTPUT\n")
    print(result["final_output"])
