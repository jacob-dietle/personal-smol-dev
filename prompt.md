# A FASTAPI based python API that uses an OpenAI GPT-4 powered Langchain Custom LLM Agent with Chatmodel and the Langchain Gmail Toolkit to interact with the Gmail API authenticating using Google Ouath2. The agent should use agent.chat(). The agent will use the Gmail Toolkit based on natural language instructions - The API sends and receives natural language tasks request from the client application layer (ChatGPT Plugin or other LLM Frontend). The API will use a simple SQLite database to store tasks and chat history.

## The high level system design is as follows in this mermaid.js diagram:
```graph LR
  subgraph SatoriIntelligentInboxAPIv1
  AGT["Agent Gmail Toolkit"]
  LCLA["Langchain Custom ChatMode LLM Agent"]
  TD["Task Database"]
  end
  GA["Gmail API"]<-->|"Programmatic API Calls"|AGT
  AGT-->|"Natural Language Tools"|LCLA
  LCLA<-->|"Natural Language API Calls"|CGP["ChatGPT Plugins or other Frontend LLM"]
  LCLA<-->|"Chat & Task Memory"|TD
```


## The API should have these endpoints:
 • POST `/api/v1/request`: Receive a natural language request from the client application, returns a requestId.
 • GET `/api/v1/request/{requestId}`: Get the status and result of a specific request.


## How to use Langchain Custom Agents & the Gmail Toolkit:

LangChain is a framework for developing applications powered by language models, enabling data-aware and agentic applications. Agents in LangChain are responsible for handling user inputs and interacting with the environment using tools. The Gmail toolkit is a set of tools that allows the agent to interact with the Gmail API and perform various email-related tasks.

Step 1: Install necessary libraries
```python
!pip install langchain
!pip install google-search-results
!pip install openai
!pip install google-api-python-client
!pip install google-auth-oauthlib
!pip install google-auth-httplib2
!pip install beautifulsoup4
```

Step 2: Import required modules
```python
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import BaseChatPromptTemplate
from langchain import SerpAPIWrapper, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import AgentAction, AgentFinish, HumanMessage
from langchain.agents.agent_toolkits import GmailToolkit
from langchain.tools.gmail.utils import build_resource_service, get_gmail_credentials
import re
from getpass import getpass
```

Step 3: Set up Gmail API credentials
Follow the Gmail API documentation to set up your credentials and download the `credentials.json` file.

Step 4: Create the GmailToolkit
```python
toolkit = GmailToolkit()
```

Step 5: Set up the PromptTemplate
Create a custom prompt template that incorporates the Gmail toolkit and chat history. Make sure to include placeholders for chat history and user input in the template.

```python
template = """Your custom template here with placeholders for chat history and user input"""

class CustomPromptTemplate(BaseChatPromptTemplate):
    # Your custom implementation of format_messages method
```

Step 6: Set up the OutputParser
Create a custom output parser that can parse the LLM output into AgentAction and AgentFinish. Define a class that inherits from AgentOutputParser and implement the `parse` method.

```python
class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Your custom implementation of the parse method
```

Step 7: Set up the LLM
```python
OPENAI_API_KEY = getpass()
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)
```

Step 8: Set up the Agent
Combine the LLM, prompt template, output parser, and Gmail toolkit to set up the custom agent. Create an instance of LLMChain with the LLM and custom prompt template. Then, create an instance of LLMSingleActionAgent with the LLMChain, custom output parser, and Gmail toolkit.

```python
llm_chain = LLMChain(llm=llm, prompt=CustomPromptTemplate())
agent = LLMSingleActionAgent(
    llm_chain=llm_chain, 
    output_parser=CustomOutputParser(),
    stop=["\nObservation:"], 
    allowed_tools=toolkit.get_tools()
)
```

Step 9: Use the Agent
Create an AgentExecutor and use it to run the custom agent with user inputs. Use the `agent.chat()` method to maintain a continuous chat functionality.

```python
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=toolkit.get_tools(), verbose=True)

while True:
    user_input = input("User: ")
    if user_input.lower() == "quit":
        break
    response = agent_executor.chat(user_input)
    print(f"Agent: {response}")
```

An Example of How to use the Gmail Toolkit: 

```
agent.run("Create a gmail draft for me to edit of a letter from the perspective of a sentient parrot"
          " who is looking to collaborate on some research with her"
          " estranged friend, a cat. Under no circumstances may you send the message, however.")
``` 

## How to use Gmail API & Google Oauth in Python:


The Gmail API is a RESTful API that enables authorized access to Gmail mailboxes and facilitates sending mail.

The API provides various resources and methods for handling mailbox functionality like messages, threads, attachments, labels, settings, and more.

**Example Endpoints**

1. `GET https://gmail.googleapis.com/gmail/v1/users/{userId}/profile`
2. `POST https://gmail.googleapis.com/gmail/v1/users/{userId}/drafts`
3. `GET https://gmail.googleapis.com/gmail/v1/users/{userId}/messages/{id}`
4. `PUT https://gmail.googleapis.com/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}`

**API Resources**

1. `v1.users`
2. `v1.users.drafts`
3. `v1.users.history`
4. `v1.users.labels`
5. `v1.users.messages`
6. `v1.users.messages.attachments`
7. `v1.users.settings` (+ multiple subresources)
8. `v1.users.threads`

We should get the Gmail ouath client_secrets from a filed called `client_secrets` in the local directory that looks like:
```{"web":{"client_id":"614374734769-jhf599tv3ie9ifrqc3qgc8th6phdhks3.apps.googleusercontent.com","project_id":"email-agent-387222","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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"}}```

**The following code snippet uses the google-auth-oauthlib.flow module to construct the authorization request.***

For example, this code requests read-only, offline access to a user's Google Drive:

```
import google.oauth2.credentials
import google_auth_oauthlib.flow

# Use the client_secret.json file to identify the application requesting
# authorization. The client ID (from that file) and access scopes are required.
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'])

# Indicate where the API server will redirect the user after the user completes
# the authorization flow. The redirect URI is required. The value must exactly
# match one of the authorized redirect URIs for the OAuth 2.0 client, which you
# configured in the API Console. If this value doesn't match an authorized URI,
# you will get a 'redirect_uri_mismatch' error.
flow.redirect_uri = 'https://www.example.com/oauth2callback'

# Generate URL for request to Google's OAuth 2.0 server.
# Use kwargs to set optional request parameters.
authorization_url, state = flow.authorization_url(
    # Enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true')
``` 

## The API should be:
- be OpenAPI compliant
- use the Tenacity library to handle rate limiting for both the OpenAI API and the Gmail API.
- Have a file called "prompt.md" that acts as the prompt for the Custom LLM Agent where we can provide it instruction. 
- Have a env. file to put our OpenAI API key, "marked insert here" 
- accessible via CLI.
- Use general best modern software engineering practices for error handling, modularity, debugging and emphasize functional programming, simplicity, straightforwardness. Written at the level of a higly experienced staff engineer. 
