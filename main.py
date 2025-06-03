from langgraph.graph import Graph
from src.agents.data_collection_agent import data_collection_agent
from src.agents.analysis_agent import analysis_agent
from src.agents.report_generation_agent import report_generation_agent

# 构建LangGraph工作流
workflow = Graph()

workflow.add_node("data_collection", data_collection_agent)
workflow.add_node("analysis", analysis_agent)
workflow.add_node("report_generation", report_generation_agent)

workflow.set_entry_point("data_collection")
workflow.add_edge("data_collection", "analysis")
workflow.add_edge("analysis", "report_generation")
workflow.set_finish_point("report_generation")

app = workflow.compile()

if __name__ == "__main__":
    # 示例运行
    user_query = "2019年1月1日至2024年12月31日特朗普上台加征关税后，对中美汇率的影响"
    result = app.invoke(user_query)
    print("\n--- 最终结果 --- ")
    print(result)
