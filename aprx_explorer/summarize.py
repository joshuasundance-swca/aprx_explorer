import typing

from langchain.chat_models.base import BaseChatModel
from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from aprx_explorer.data_models import GPHistory

default_system_message = """
You are a text generation AI that interprets geoprocessing history objects from ArcGIS Pro.
Provide a concise natural language summary of the geoprocessing history object with no additional commentary.
"""

default_human_message = """
```xml
{propertiesXML}
```
"""


def get_chain(
    llm: BaseChatModel,
    system_message: str = default_system_message,
    human_message: str = default_human_message,
) -> Runnable:  # type: ignore
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message.strip()),
            ("human", human_message.strip()),
        ],
    )

    if prompt.input_variables != ["propertiesXML"]:
        raise ValueError(
            "The prompt must have exactly one input variable: propertiesXML",
        )

    chain = (
        (lambda history: {"propertiesXML": history.propertiesXML})
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def add_summaries(
    history: typing.Iterable[GPHistory],
    llm: BaseChatModel,
    system_message: str = default_system_message,
    human_message: str = default_human_message,
) -> list[GPHistory]:
    chain = get_chain(llm, system_message, human_message)
    responses = chain.batch(list(history))
    return [
        GPHistory(
            **h.model_dump(),
            text=response,
        )
        for h, response in zip(history, responses)
    ]
