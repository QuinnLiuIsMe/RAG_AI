from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from app.tools.calculator import calculator
from app.tools.metrics import compute_error_rate

def build_agent():
    llm = ChatTongyi(
        model="qwen-max",
        temperature=0
    )

    tools = [calculator, compute_error_rate]

    prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an operations AI agent. You can use the provided tools to help answer questions."),
            ("human", "{input}\n{agent_scratchpad}")
        ])

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )

    return agent_executor
