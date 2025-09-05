"""
title: Prompt Enhancer
author: Haervwe
author_url: https://github.com/Haervwe
funding_url: https://github.com/Haervwe/open-webui-tools
version: 0.5.2
important note: if you are going to sue this filter with custom pipes, do not use the show enhanced prompt valve setting
"""

import logging
from pydantic import BaseModel, Field
from typing import Callable, Awaitable, Any, Optional
import json
from dataclasses import dataclass
from fastapi import Request
from open_webui.utils.chat import generate_chat_completion
from open_webui.utils.misc import get_last_user_message
from open_webui.models.models import Models
from open_webui.models.users import User
from open_webui.routers.models import get_models

name = "enhancer"


def setup_logger():
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.set_name(name)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = setup_logger()


class Filter:
    class Valves(BaseModel):
        user_customizable_template: str = Field(
            default="""
You are an elite prompt engineering specialist with expertise in optimizing and refining prompts for maximum effectiveness for a research assistant. 
You specialize in all prompt engineering best practices. 
Your mission is to transform basic prompts into messages that are more relevant to the conversation using the rest of the conversation as context while keeping the message as similar to the original as possible. 

When enhancing prompts:
1. Analyze the intent behind the original prompt using the context of the conversation. 
2. Make as few changes as possible to the original message but modify it as necessary so it is more relevant to the context. 


Deliver only the new prompt without any explanations, introductions, or meta-commentary. Follow prompt engineering best practices.

""",
            description="Prompt to use in the Prompt enhancer System Message",
        )
        show_status: bool = Field(
            default=False,
            description="Show status indicators",
        )
        show_enhanced_prompt: bool = Field(
            default=False,
            description="Show Enhanced Prompt in chat",
        )
        model_id: Optional[str] = Field(
            default=None,
            description="Model to use for the prompt enhancement, leave empty to use the same as selected for the main response.",
        )
        append_knowledge_to_messages: bool = Field(
            default=False,
            description="If checked, append the list of knowledge to the first user message in the conversation",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.__current_event_emitter__ = None
        self.__user__ = None
        self.__model__ = None
        self.__request__ = None

    def extract_model_knowledge(self, model_data: dict) -> list:
        """Extract knowledge information from the model's metadata"""
        knowledge_items = []

        logger.debug("Extracting knowledge from model data")
        logger.debug(
            f"Model data keys: {model_data.keys() if isinstance(model_data, dict) else 'Not a dict'}"
        )

        # Check if model has knowledge in meta
        if isinstance(model_data, dict):
            meta = model_data.get("meta", {})
            if isinstance(meta, dict):
                knowledge = meta.get("knowledge", [])
                logger.debug(f"Found knowledge in meta: {knowledge}")

                if isinstance(knowledge, list):
                    for knowledge_item in knowledge:
                        if isinstance(knowledge_item, dict):
                            name = knowledge_item.get("name", "Unknown Knowledge")
                            description = knowledge_item.get(
                                "description", "No description available"
                            )

                            # If description is empty or same as name, provide a default
                            if (
                                not description
                                or description.strip() == ""
                                or description == name
                            ):
                                description = "Knowledge base content"

                            knowledge_items.append(
                                {"name": name, "description": description}
                            )
                            logger.debug(
                                f"Added knowledge item: {name} - {description}"
                            )

        logger.debug(f"Final extracted knowledge items: {knowledge_items}")
        return knowledge_items

    def format_knowledge_list(self, knowledge_items: list) -> str:
        """Format knowledge items into the specified format"""
        if not knowledge_items:
            return ""

        formatted_lines = ["\n### Knowledgebases"]
        for item in knowledge_items:
            name = item.get("name", "Unknown")
            description = item.get("description", "No description available")
            formatted_lines.append(f"**{name}:**")
            formatted_lines.append(f"   - {description}")

        return "\n".join(formatted_lines)

    def is_first_user_message(self, messages: list) -> bool:
        """Check if this is the first user message in the conversation"""
        user_message_count = 0
        for msg in messages:
            if msg.get("role") == "user":
                user_message_count += 1

        # If there's only 1 user message, this is the first one
        return user_message_count == 1

    async def inlet(
        self,
        body: dict,
        __event_emitter__: Callable[[Any], Awaitable[None]],
        __user__: Optional[dict] = None,
        __model__: Optional[dict] = None,
        __request__: Optional[Request] = None,
        __files__: Optional[list] = None,
    ) -> dict:
        self.__current_event_emitter__ = __event_emitter__
        self.__request__ = __request__
        self.__model__ = __model__
        self.__user__ = User(**__user__) if isinstance(__user__, dict) else __user__

        # Debug: Log the __model__ parameter to understand its structure
        logger.debug("__model__ parameter received:")
        logger.debug(
            json.dumps(__model__, indent=2, default=str) if __model__ else "None"
        )

        # Fetch available models and log their relevant details
        available_models = await get_models(self.__request__, self.__user__)
        logger.debug("Available Models (truncated image data):")

        # Find the current model being used
        current_model_id = body.get("model")
        current_model_data = None

        for model in available_models:
            model_dict = model.model_dump()  # Convert to dict for modification

            # Check if this is the current model
            if model_dict.get("id") == current_model_id:
                current_model_data = model_dict
                logger.debug(f"Found current model: {current_model_id}")

            # Truncate sensitive data for logging
            if "meta" in model_dict:
                if isinstance(model_dict["meta"], dict):
                    if "profile_image_url" in model_dict["meta"]:
                        model_dict["meta"]["profile_image_url"] = (
                            model_dict["meta"]["profile_image_url"][:50] + "..."
                            if isinstance(model_dict["meta"]["profile_image_url"], str)
                            else None
                        )
                    if (
                        "user" in model_dict
                        and "profile_image_url" in model_dict["user"]
                    ):
                        model_dict["user"]["profile_image_url"] = (
                            model_dict["user"]["profile_image_url"][:50] + "..."
                            if isinstance(model_dict["user"]["profile_image_url"], str)
                            else None
                        )
                else:
                    logger.warning(
                        f"Unexpected type for model.meta: {type(model_dict['meta'])}"
                    )
            else:
                logger.warning("Model missing 'meta' key: %s", model.id)

            # Truncate files information for logging
            if "knowledge" in model_dict and isinstance(model_dict["knowledge"], list):
                for knowledge_item in model_dict["knowledge"]:
                    if isinstance(knowledge_item, dict) and "files" in knowledge_item:
                        knowledge_item["files"] = "List of files (truncated)"

            logger.debug(json.dumps(model_dict, indent=2))

        messages = body["messages"]
        user_message = get_last_user_message(messages)

        # Extract knowledge from the current model
        knowledge_items = []
        if current_model_data:
            knowledge_items = self.extract_model_knowledge(current_model_data)
        elif __model__:
            # Fallback to __model__ parameter if available
            knowledge_items = self.extract_model_knowledge(__model__)

        # Handle appending knowledge to first user message if valve is enabled
        if self.valves.append_knowledge_to_messages and knowledge_items:
            if self.is_first_user_message(messages):
                logger.debug(
                    "This is the first user message and append_knowledge_to_messages is enabled"
                )
                formatted_knowledge = self.format_knowledge_list(knowledge_items)

                # Find the last user message and append knowledge to it
                for i in range(len(messages) - 1, -1, -1):
                    if messages[i].get("role") == "user":
                        original_content = messages[i]["content"]
                        messages[i][
                            "content"
                        ] = f"{original_content}{formatted_knowledge}"
                        logger.debug(
                            f"Appended knowledge to first user message: {messages[i]['content']}"
                        )
                        break

                # Update the body with modified messages
                body["messages"] = messages
                # Update user_message since we modified it
                user_message = get_last_user_message(messages)

        if self.valves.show_status:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "Enhancing the prompt...",
                        "done": False,
                    },
                }
            )

        # Prepare context from chat history, excluding the last user message
        context_messages = [
            msg
            for msg in messages
            if msg["role"] != "user" or msg["content"] != user_message
        ]
        context = "\n".join(
            [f"{msg['role'].upper()}: {msg['content']}" for msg in context_messages]
        )

        # Build context block
        context_str = f'\n\nContext:\n"""{context}"""\n\n' if context else ""

        # Build knowledge information block (only for enhancement prompt, not for appending to user message)
        knowledge_str = ""
        if knowledge_items and not self.valves.append_knowledge_to_messages:
            formatted_knowledge = self.format_knowledge_list(knowledge_items)
            knowledge_str = f"\n\nAttached Knowledge:\n{formatted_knowledge}\n\n"
            logger.debug(f"Knowledge string to be included: {knowledge_str}")

        # Construct the system prompt with clear delimiters
        system_prompt = self.valves.user_customizable_template

        # Add instruction about knowledge if it exists and we're not appending to messages
        if knowledge_items and not self.valves.append_knowledge_to_messages:
            system_prompt += """
IMPORTANT: When enhancing the prompt, if the user references 'attached knowledge', 'knowledge base', 'uploaded knowledge', or similar terms, you MUST replace these generic references with the specific formatted knowledge list below. Use this EXACT format:

#### Knowledgebases
 - **{name_of_knowledge1}**
 - **{name_of_knowledge2}**
 - **{name_of_knowledge3}**

Do NOT just list the knowledge names in a sentence. Use the structured format above."""

        user_prompt = (
            f"Context: {context_str}"
            f"{knowledge_str}"
            f'Prompt to enhance:\n"""{user_message}"""\n\n'
        )

        # Log the system prompt before sending to LLM
        logger.debug("System Prompt: %s", system_prompt)
        logger.debug("User Prompt: %s", user_prompt)

        # Determine the model to use
        model_to_use = None
        if self.valves.model_id:
            model_to_use = self.valves.model_id
        else:
            model_to_use = body["model"]

        # Check if the selected model has "-pipe" or "pipe" in its name.
        is_pipeline_model = False
        if "-pipe" in model_to_use.lower() or "pipe" in model_to_use.lower():
            is_pipeline_model = True
            logger.warning(
                f"Selected model '{model_to_use}' appears to be a pipeline model.  Consider using the base model."
            )

        # If a pipeline model is *explicitly* chosen, use it. Otherwise, fall back to the main model.
        if not self.valves.model_id and is_pipeline_model:
            logger.warning(
                f"Pipeline model '{model_to_use}' selected without explicit model_id.  Using main model instead."
            )
            model_to_use = body["model"]  # Fallback to main model
            is_pipeline_model = False

        # Construct payload for LLM request
        payload = {
            "model": model_to_use,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"{user_prompt}",
                },
            ],
            "stream": False,
        }

        try:
            # Use the User object directly, as done in other scripts
            logger.debug(
                "API CALL:\n Request: %s\n Form_data: %s\n User: %s",
                str(self.__request__),
                json.dumps(payload, indent=2),
                self.__user__,
            )

            response = await generate_chat_completion(
                self.__request__, payload, user=self.__user__, bypass_filter=True
            )

            enhanced_prompt = response["choices"][0]["message"]["content"]
            logger.debug("Enhanced prompt: %s", enhanced_prompt)

            # Update the messages with the enhanced prompt
            messages[-1]["content"] = enhanced_prompt
            body["messages"] = messages

            if self.valves.show_status:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Prompt successfully enhanced.",
                            "done": True,
                        },
                    }
                )
            if self.valves.show_enhanced_prompt:
                enhanced_prompt_message = f"<details>\n<summary>Enhanced Prompt</summary>\n{enhanced_prompt}\n\n---\n\n</details>"
                await __event_emitter__(
                    {
                        "type": "message",
                        "data": {
                            "content": enhanced_prompt_message,
                        },
                    }
                )

        except ValueError as ve:
            logger.error("Value Error: %s", str(ve))
            if self.valves.show_status:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Error: {str(ve)}",
                            "done": True,
                        },
                    }
                )
        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            if self.valves.show_status:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "An unexpected error occurred.",
                            "done": True,
                        },
                    }
                )

        return body

    async def outlet(
        self,
        body: dict,
        __event_emitter__: Callable[[Any], Awaitable[None]],
        __user__: Optional[dict] = None,
        __model__: Optional[dict] = None,
        __request__: Optional[Request] = None,
    ) -> dict:
        self.__current_event_emitter__ = __event_emitter__
        self.__request__ = __request__
        self.__model__ = __model__
        self.__user__ = User(**__user__) if isinstance(__user__, dict) else __user__
        print(body)
        return body
