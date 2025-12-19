from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from backend import chatbot
# --- Initialize Flask App ---
app = Flask(__name__)


def get_chatbot_response(chatbot, user_message: str) -> str:
    """
    Call the chatbot with a user message and return only the final AI response.
    """
    try:
        # Get final state from chatbot
        final_state = chatbot.invoke({"messages": [HumanMessage(content = user_message)]},config = {'configurable':{'thread_id':1}}
)

        # Extract messages from state
        messages = final_state.get("messages", [])

        if not messages:
            return "⚠️ Koi response nahi mila."

        # Get last message (should be AIMessage)
        response_message = messages[-1]

        if isinstance(response_message, AIMessage):
            full_response_text = response_message.content.strip()

            # Remove echo if AI starts by repeating user input
            user_message_lower = user_message.strip().lower()
            response_lower = full_response_text.lower()

            if response_lower.startswith(user_message_lower):
                end_index = response_lower.find(user_message_lower) + len(user_message_lower)
                clean_response = full_response_text[end_index:].strip()
                return clean_response if clean_response else full_response_text
            else:
                return full_response_text

        else:
            print(f"[Warning] Unexpected message type: {type(response_message)}")
            return "⚠️ Mujhe sahi response nahi mila."

    except Exception as e:
        print(f"[Error] LLM call failed: {e}")
        return "⚠️ Maaf kijiye, LLM se jawab milne mein koi samasya aa gayi."

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.form.get('Body')
    sender_number = request.form.get('From') 

    if not incoming_msg:
        print("Received empty message from WhatsApp.")
        return "OK", 200 

    print(f"Received from {sender_number}: '{incoming_msg}'")

    llm_output = get_chatbot_response(chatbot,incoming_msg)

    print(f"Sending to LLM: '{incoming_msg}'")
    print(f"LLM Response: '{llm_output}'")

    
    resp = MessagingResponse()
    msg = resp.message(llm_output) 

    return str(resp) 

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
