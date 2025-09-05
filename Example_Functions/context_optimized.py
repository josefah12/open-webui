import requests
import json
import openai
import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union, Callable, Awaitable


class Filter:
    """
    1. Uses the selected LLM and context to determine if a web search is needed and what type ("news search" or "summary") using OpenAI structured outputs and explicit reasoning guidelines.
    2. If needed, generates an optimized search query for the correct search type.
    3. Uses this query for a search via Brave API (news or summary endpoint).
    4. Adds the summary or search results to the LLM request.
    5. Emits status updates to the user when searching with Brave, controlled by SHOW_BRAVE_STATUS.
    6. Emits a separate event for whether a search is required, controlled by SHOW_SEARCH_NEEDED_STATUS.
    """

    class Valves(BaseModel):
        OPENAI_API_KEY: str = Field(default="", description="Your OpenAI API key")
        OPENAI_MODEL: str = Field(
            default="gpt-4.1-mini", description="OpenAI model to use"
        )
        MAX_CHAT_HISTORY: int = Field(
            default=5, description="Number of past user messages to analyze"
        )
        BRAVE_API_KEY: str = Field(default="", description="Your Brave Search API key")
        INCLUDE_SOURCES: bool = Field(
            default=True, description="Include source URLs in the summary"
        )
        NUM_FALLBACK_RESULTS: int = Field(
            default=3, description="Number of web results if no summary"
        )
        MAX_SUMMARY_LENGTH: int = Field(
            default=2000, description="Maximum summary length"
        )
        DEBUG_MODE: bool = Field(default=True, description="Enable debug output")
        OUTPUT_MESSAGE: str = Field(
            default="",
            description="Message to append to response",
        )
        SUMMARY_PREFIX: str = Field(
            default="\n\nWeb search summary:\n", description="Prefix for search summary"
        )
        RESULTS_PREFIX: str = Field(
            default="\n\nWeb search results:\n", description="Prefix for search results"
        )
        SHOW_BRAVE_STATUS: bool = Field(
            default=True, description="Emit status events for Brave search"
        )
        SHOW_SEARCH_NEEDED_STATUS: bool = Field(
            default=True, description="Emit event for whether search is required"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.debug_log = []
        self.__event_emitter__: Optional[Callable[[dict], Awaitable[None]]] = None
        self.__search_needed_emitter__: Optional[Callable[[dict], Awaitable[None]]] = (
            None
        )

    def _log_debug(self, message: str):
        if self.valves.DEBUG_MODE:
            self.debug_log.append(message)

    def _extract_recent_user_messages(self, messages: List[Dict]) -> List[Dict]:
        user_messages = []
        for message in messages:
            if message.get("role") == "user" and "content" in message:
                user_messages.append({"role": "user", "content": message["content"]})
        max_messages = min(len(user_messages), self.valves.MAX_CHAT_HISTORY)
        return user_messages[-max_messages:]

    async def _emit_status(self, description: str, done: bool = False):
        if self.valves.SHOW_BRAVE_STATUS and self.__event_emitter__:
            await self.__event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": description,
                        "done": done,
                    },
                }
            )

    async def _emit_search_needed(self, needed: bool, search_type: Optional[str]):
        if self.valves.SHOW_SEARCH_NEEDED_STATUS and self.__search_needed_emitter__:
            await self.__search_needed_emitter__(
                {
                    "type": "search_needed",
                    "data": {
                        "needed": needed,
                        "search_type": search_type,
                        "description": (
                            f"Web search required: {needed}, type: {search_type}"
                        ),
                    },
                }
            )

    def _llm_decide_web_search_and_type(
        self, user_messages: List[Dict], current_query: str
    ) -> Dict[str, Any]:
        if not self.valves.OPENAI_API_KEY:
            self._log_debug(
                "ERROR: No OpenAI API key provided, defaulting to summary search needed."
            )
            return {"needed": True, "search_type": "summary"}

        try:
            client = openai.OpenAI(api_key=self.valves.OPENAI_API_KEY)
            current_date = datetime.date.today().isoformat()
            guidelines = (
                "## Guidelines for When to Use Search vs No Search for Answering Queries\n"
                "### Requires Search (needed: true)\n"
                "- Queries involving current events, news, or recent developments.\n"
                "- Requests for real-time data such as stock prices, weather updates, or sports scores.\n"
                "- Inquiries about code, scripting, or programming (e.g. Python SDKs, PowerShell, C# etc.\n"
                "- Inquiries about recent software updates, releases, or technical documentation.\n"
                "- User specifically asks for the latest updates on a topic.\n"
                "- Any time-sensitive information that changes frequently.\n"
                "- Specific facts about recent events occurring after the knowledge cutoff date.\n\n"
                "### Search Types\n"
                "- news search: For breaking news, current events, recent headlines, and political developments.\n"
                "- summary: For technical documentation, product information, general web content, and how-to guides.\n\n"
                "### No Search Required (needed: false)\n"
                "- Questions related to general knowledge, historical facts, locations, or well-established concepts.\n"
                "- Requests involving mathematical calculations or logical reasoning.\n"
                "- Creative tasks such as writing, brainstorming, or analysis.\n"
                "- Questions answerable from the existing conversation context.\n"
            )
            prompt_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant that determines if a web search is needed to answer the user's latest question. "
                        "Analyze the conversation history and the current query. "
                        "Use the following guidelines to make your decision:\n"
                        f"{guidelines}\n"
                        "If a search is needed, respond with a JSON object ONLY in this format:\n"
                        "{\n"
                        '  "needed": true|false,\n'
                        '  "search_type": "news search"|"summary"|null\n'
                        "}\n"
                        "If a search is needed, set 'needed' to true and 'search_type' to either 'news search' (for current events, headlines, or news topics) or 'summary' (for general web summaries). "
                        "If no search is needed, set 'needed' to false and 'search_type' to null. "
                        "Do not include any explanation or extra text. Today's date is "
                        f"{current_date}."
                    ),
                }
            ]
            prompt_messages.extend(user_messages[:-1])
            prompt_messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Does the following query require a web search to answer accurately? Query: '{current_query}'"
                    ),
                }
            )
            self._log_debug(
                f"Sending web search/type decision request to OpenAI with {len(prompt_messages)} messages"
            )
            response = client.chat.completions.create(
                model=self.valves.OPENAI_MODEL,
                messages=prompt_messages,
                temperature=0,
                max_tokens=80,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content.strip()
            self._log_debug(f"Web search/type decision LLM output: '{content}'")
            try:
                result = json.loads(content)
                needed = bool(result.get("needed", False))
                search_type = result.get("search_type", None)
                if search_type not in ("news search", "summary", None):
                    search_type = None
                return {"needed": needed, "search_type": search_type}
            except Exception as e:
                self._log_debug(f"Error parsing LLM JSON output: {e}")
                return {"needed": True, "search_type": "summary"}
        except Exception as e:
            error_msg = f"Error determining need/type for web search: {str(e)}"
            self._log_debug(error_msg)
            return {"needed": True, "search_type": "summary"}

    def _generate_optimized_query(
        self, user_messages: List[Dict], current_query: str, search_type: str
    ) -> str:
        if not self.valves.OPENAI_API_KEY:
            self._log_debug("ERROR: No OpenAI API key provided, using original query")
            return current_query

        try:
            client = openai.OpenAI(api_key=self.valves.OPENAI_API_KEY)
            current_date = datetime.date.today().isoformat()
            prompt_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a search query optimizer. Your task is to analyze the "
                        "conversation history and the current query, then generate an optimized search query that will "
                        "provide the most relevant information. Focus on extracting key concepts and search terms. "
                        "IMPORTANT: Return ONLY the optimized search query without any explanations or additional text."
                    ),
                }
            ]
            prompt_messages.extend(user_messages[:-1])
            prompt_messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Based on our conversation history, create an optimized search query for: "
                        f"'{current_query}' that is accurate as of {current_date} and suitable for a {search_type}."
                    ),
                }
            )
            self._log_debug(
                f"Sending request to OpenAI with {len(prompt_messages)} messages"
            )
            response = client.chat.completions.create(
                model=self.valves.OPENAI_MODEL,
                messages=prompt_messages,
                temperature=0.3,
                max_tokens=100,
            )
            optimized_query = response.choices[0].message.content.strip()
            self._log_debug(f"Original query: '{current_query}'")
            self._log_debug(f"Optimized query: '{optimized_query}'")
            return optimized_query
        except Exception as e:
            error_msg = f"Error generating optimized query: {str(e)}"
            self._log_debug(error_msg)
            return current_query

    def _get_brave_search(self, query: str, search_type: str) -> Dict[str, Any]:
        self._log_debug(
            f"Starting Brave search for query: '{query}', type: '{search_type}'"
        )
        if not self.valves.BRAVE_API_KEY:
            self._log_debug("ERROR: No Brave API key provided")
            return {"error": "No API key provided"}

        if search_type == "news search":
            endpoint = "https://api.search.brave.com/res/v1/news/search"
            params = {
                "q": query,
                "count": 10,
                "country": "us",
                "search_lang": "en",
                "spellcheck": 1,
            }
        else:  # summary (default)
            endpoint = "https://api.search.brave.com/res/v1/web/search"
            params = {
                "q": query,
                "summary": 1,
                "count": 5,
                "country": "DE",
                "search_lang": "de",
                "safesearch": "off",
            }

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.valves.BRAVE_API_KEY,
            "Api-Version": "2023-10-11",
        }
        self._log_debug(f"Brave API request: {endpoint} with params {params}")
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            status_code = response.status_code
            self._log_debug(f"Brave API response status: {status_code}")
            data = response.json()
            self._log_debug(f"Brave response keys: {list(data.keys())}")
            return data
        except Exception as e:
            error_msg = f"Error performing Brave search: {str(e)}"
            self._log_debug(error_msg)
            return {"error": error_msg}

    def _get_summary(self, summary_key: str) -> Dict[str, Any]:
        self._log_debug(f"Starting summary request with key: {summary_key}")
        if not summary_key:
            return {"error": "No summary key provided"}
        endpoint = "https://api.search.brave.com/res/v1/summarizer/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.valves.BRAVE_API_KEY,
            "Api-Version": "2024-04-23",
        }
        params = {"key": summary_key, "entity_info": 1}
        self._log_debug(f"Summary API request: {endpoint} with key={summary_key}")
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            status_code = response.status_code
            self._log_debug(f"Summary API response status: {status_code}")
            data = response.json()
            self._log_debug(f"Summary response keys: {list(data.keys())}")
            return data
        except Exception as e:
            error_msg = f"Error getting Brave summary: {str(e)}"
            self._log_debug(error_msg)
            return {"error": error_msg}

    def _format_news_results(
        self, news_data: Dict[str, Any], num_results: int = 5
    ) -> str:
        if "results" not in news_data or not news_data["results"]:
            return f"{self.valves.RESULTS_PREFIX}No news results available."
        results = news_data["results"][:num_results]
        formatted_text = self.valves.RESULTS_PREFIX
        for i, result in enumerate(results):
            formatted_text += f"{i+1}. {result.get('title', 'No title')}\n"
            if "description" in result:
                formatted_text += f"{result['description']}\n"
            formatted_text += f"Source: {result.get('url', 'No URL')}\n\n"
        return formatted_text

    def _format_web_results(
        self, web_data: Dict[str, Any], num_results: int = 3
    ) -> str:
        if (
            "web" not in web_data
            or "results" not in web_data["web"]
            or not web_data["web"]["results"]
        ):
            return f"{self.valves.RESULTS_PREFIX}No web results available."
        results = web_data["web"]["results"][:num_results]
        formatted_text = self.valves.RESULTS_PREFIX
        for i, result in enumerate(results):
            formatted_text += f"{i+1}. {result.get('title', 'No title')}\n"
            if "description" in result:
                formatted_text += f"{result['description']}\n"
            formatted_text += f"Source: {result.get('url', 'No URL')}\n\n"
        return formatted_text

    def _extract_summary_content(self, summary_obj: Union[List, Dict, Any]) -> str:
        if isinstance(summary_obj, list) and len(summary_obj) > 0:
            first_item = summary_obj[0]
            if isinstance(first_item, dict) and "data" in first_item:
                return first_item["data"]
            try:
                return "".join(str(item) for item in summary_obj)
            except:
                pass
        elif isinstance(summary_obj, dict) and "content" in summary_obj:
            return summary_obj["content"]
        return ""

    def _format_summary_content(
        self, summary_data: Dict[str, Any], web_data: Dict[str, Any]
    ) -> str:
        self._log_debug("Formatting summary content")
        if "error" in summary_data:
            self._log_debug(f"Error found: {summary_data['error']}")
            return self._format_web_results(web_data, self.valves.NUM_FALLBACK_RESULTS)
        content = ""
        if "summary" in summary_data:
            content = self._extract_summary_content(summary_data["summary"])
        if content:
            self._log_debug(
                f"Successfully extracted summary content ({len(content)} chars)"
            )
            formatted_text = self.valves.SUMMARY_PREFIX
            if len(content) > self.valves.MAX_SUMMARY_LENGTH:
                content = content[: self.valves.MAX_SUMMARY_LENGTH] + "..."
            formatted_text += content
            if self.valves.INCLUDE_SOURCES:
                citations = []
                if "citations" in summary_data.get("summary", {}):
                    citations = summary_data["summary"]["citations"]
                elif (
                    "enrichments" in summary_data
                    and "citations" in summary_data["enrichments"]
                ):
                    citations = summary_data["enrichments"]["citations"]
                if citations:
                    formatted_text += "\n\nSources:\n"
                    for i, citation in enumerate(citations):
                        if "url" in citation:
                            formatted_text += f"{i+1}. {citation.get('url')}\n"
            return formatted_text
        else:
            self._log_debug("No summary content available, falling back to web results")
            return self._format_web_results(web_data, self.valves.NUM_FALLBACK_RESULTS)

    async def inlet(
        self,
        body: dict,
        __event_emitter__: Optional[Callable[[dict], Awaitable[None]]] = None,
        __search_needed_emitter__: Optional[Callable[[dict], Awaitable[None]]] = None,
    ) -> dict:
        """
        Process user query with chat history analysis and Brave search.
        Emits status events if enabled in valves.
        Emits a separate event for whether a search is required.
        """
        self.debug_log = []
        self.__event_emitter__ = __event_emitter__
        self.__search_needed_emitter__ = __search_needed_emitter__
        self._log_debug("=== Starting new enhanced search request ===")

        if "messages" in body and body["messages"]:
            latest_message = body["messages"][-1]
            if latest_message.get("role") == "user" and "content" in latest_message:
                original_query = latest_message["content"]
                if original_query.strip():
                    user_messages = self._extract_recent_user_messages(body["messages"])
                    self._log_debug(
                        f"Extracted {len(user_messages)} recent user messages for context"
                    )

                    # Use LLM to decide if a web search is needed and what type
                    decision = self._llm_decide_web_search_and_type(
                        user_messages, original_query
                    )
                    needs_web_search = decision.get("needed", True)
                    search_type = decision.get("search_type", "summary")
                    self._log_debug(
                        f"LLM decision: needs_web_search={needs_web_search}, search_type={search_type}"
                    )

                    # Emit search-needed event if enabled
                    await self._emit_search_needed(needs_web_search, search_type)

                    if not needs_web_search:
                        self._log_debug("Web search not needed, skipping Brave search.")
                        await self._emit_status(
                            "Web search not needed for this query.", done=True
                        )
                        return body

                    # Generate optimized query with OpenAI if we have an API key
                    if self.valves.OPENAI_API_KEY:
                        optimized_query = self._generate_optimized_query(
                            user_messages, original_query, search_type
                        )
                        search_query = optimized_query
                    else:
                        search_query = original_query
                        self._log_debug(
                            "No OpenAI API key provided, using original query"
                        )

                    # Emit: Starting Brave search if enabled
                    await self._emit_status(
                        f"Searching with Brave ({search_type}): '{search_query}'",
                        done=False,
                    )

                    brave_data = self._get_brave_search(search_query, search_type)

                    if "error" in brave_data:
                        self._log_debug(f"Brave search error: {brave_data['error']}")
                        await self._emit_status(
                            f"Brave search failed: {brave_data['error']}", done=True
                        )
                        formatted_results = f"{self.valves.RESULTS_PREFIX}Failed to perform search: {brave_data['error']}"
                    else:
                        if search_type == "news search":
                            formatted_results = self._format_news_results(
                                brave_data, num_results=5
                            )
                            await self._emit_status(
                                "Brave news search complete.", done=True
                            )
                        else:  # summary
                            summary_key = brave_data.get("summarizer", {}).get("key")
                            if summary_key:
                                await self._emit_status(
                                    "Retrieving summary from Brave...", done=False
                                )
                                summary_data = self._get_summary(summary_key)
                                formatted_results = self._format_summary_content(
                                    summary_data, brave_data
                                )
                                await self._emit_status(
                                    "Brave search summary complete.", done=True
                                )
                            else:
                                self._log_debug(
                                    "No summary key available, falling back to web results"
                                )
                                formatted_results = self._format_web_results(
                                    brave_data, self.valves.NUM_FALLBACK_RESULTS
                                )
                                await self._emit_status(
                                    "Brave search complete (no summary).", done=True
                                )

                    if search_query != original_query:
                        query_info = f'\n\nOptimized search query: "{search_query}"\n'
                        formatted_results = query_info + formatted_results

                    self._log_debug("Appending search results to user message")
                    latest_message["content"] += formatted_results

        return body

    def stream(self, event: dict) -> dict:
        return event

    def outlet(self, body: dict) -> dict:
        if "messages" in body and body["messages"]:
            last_assistant_message = None
            for message in body["messages"]:
                if message.get("role") == "assistant" and "content" in message:
                    last_assistant_message = message
            if last_assistant_message:
                last_assistant_message["content"] += self.valves.OUTPUT_MESSAGE
                if self.valves.DEBUG_MODE and self.debug_log:
                    debug_text = "\n\n=== DEBUG LOG ===\n"
                    for i, log in enumerate(self.debug_log, 1):
                        debug_text += f"{i}. {log}\n"
                    last_assistant_message["content"] += debug_text
        return body
