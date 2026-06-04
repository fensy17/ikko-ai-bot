import os
import json
from openai import OpenAI
from iiko_api import IikoClient

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
iiko = IikoClient()

def get_iiko_organizations():
    data = iiko.get_organizations()
    orgs = data.get("organizations", [])

    if not orgs:
        return "Организации не найдены."

    text = "Организации iiko:\n"
    for org in orgs:
        text += f"- {org.get('name')} | ID: {org.get('id')}\n"

    return text

tools = [
    {
        "type": "function",
        "name": "get_iiko_organizations",
        "description": "Получить список организаций из iiko Cloud API.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

def ask_agent(user_text: str) -> str:
    response = client.responses.create(
        model="gpt-5",
        input=[
            {
                "role": "system",
                "content": """
Ты AI-ассистент ресторана Палуба, подключенный к iiko.
Отвечай кратко и по делу.
Если пользователь просит данные из iiko — используй доступные функции.
Опасные действия вроде создания товаров, накладных, списаний и инвентаризаций нельзя выполнять без подтверждения пользователя.
"""
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        tools=tools
    )

    for item in response.output:
        if item.type == "function_call":
            if item.name == "get_iiko_organizations":
                result = get_iiko_organizations()

                second_response = client.responses.create(
                    model="gpt-5",
                    input=[
                        {
                            "role": "user",
                            "content": user_text
                        },
                        item,
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": result
                        }
                    ]
                )

                return second_response.output_text

    return response.output_text
