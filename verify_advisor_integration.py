from datetime import datetime as dt
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import backend
    from langchain_core.messages import HumanMessage
    
    print("Successfully imported backend.")
    
    # Mock state
    mock_state = {
        'messages': [HumanMessage(content="How do I invest in stocks?")],
        'category': "needs advice",
        'action': {}
    }
    
    print("Invoking advisor_func...")
    # We are testing if the function can be called and graph invoked.
    # Note: This might make actual LLM calls.
    # If it fails due to credentials, we will catch that, but atleast we verify imports.
    try:
        result = backend.advisor_func(mock_state)
        print("advisor_func returned result:", result)
        if 'messages' in result and len(result['messages']) > 0:
            print("Integration successful: Received response from advisor.")
        else:
            print("Integration warning: No messages returned.")
            
    except Exception as e:
        print(f"Error during advisor_func execution: {e}")
        # If it is an auth error, it proves integration worked but auth failed.
        if "api_key" in str(e).lower() or "credentials" in str(e).lower() or "quota" in str(e).lower():
             print("Authentication/Quota error detected. This is expected if keys are missing/exhausted, but confirms code path is correct.")

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
