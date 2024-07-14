import os
import logging
import dialogflow
from flask import Flask, request, jsonify, render_template
from google.protobuf.json_format import MessageToDict
from util import get_order_status, get_str_from_food_dict, extract_session_id, insert_order_item, get_next_order_id, get_order_total, insert_order_tracking

app = Flask(__name__)

inprogress_order = {}

logging.basicConfig(level=logging.DEBUG)

def detect_intent_with_parameters(project_id, session_id, query_params, language_code, user_input):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=user_input, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input, query_params=query_params)
    return response

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/chat', methods=["POST"])
def chat():
    input_text = request.form['message']

    GOOGLE_AUTHENTICATION_FILE_NAME = "credentials/key.json"
    current_directory = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(current_directory, GOOGLE_AUTHENTICATION_FILE_NAME)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

    GOOGLE_PROJECT_ID = "chatbot-qsod"
    session_id = "1234567891"
    context_short_name = "does_not_matter"

    context_name = "projects/" + GOOGLE_PROJECT_ID + "/agent/sessions/" + session_id + "/contexts/" + context_short_name.lower()

    parameters = dialogflow.types.struct_pb2.Struct()

    context_1 = dialogflow.types.context_pb2.Context(
        name=context_name,
        lifespan_count=2,
        parameters=parameters
    )
    query_params_1 = {"contexts": [context_1]}

    language_code = 'en'

    response = detect_intent_with_parameters(
        project_id=GOOGLE_PROJECT_ID,
        session_id=session_id,
        query_params=query_params_1,
        language_code=language_code,
        user_input=input_text
    )
    result = MessageToDict(response)
    print(result)
    if len(result['queryResult']['fulfillmentMessages']) == 2:
        response = {"message": result['queryResult']['fulfillmentText'],
                    "payload": result['queryResult']['fulfillmentMessages'][1]['payload']}
    else:
        response = {"message": result['queryResult']['fulfillmentText'], "payload": None}
    return jsonify(response)

def track_order(parameters: dict, session_id):
    order_id = int(parameters["number"])
    status = get_order_status(order_id)

    if status:
        fulfillment_text = f"The order status for order id {order_id} is {status}"
    else:
        fulfillment_text = f"No order found with order id {order_id}"

    return jsonify({"fulfillmentText": fulfillment_text})

def add_order(parameters: dict, session_id):
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry, I don't understand. Please specify food items and quantities clearly."
        return jsonify({"fulfillmentText": fulfillment_text})
    else:
        new_food_dict = dict(zip(food_items, quantities))
        if session_id in inprogress_order:
            result = {}
            for key in inprogress_order[session_id].keys() | new_food_dict.keys():
                result[key] = inprogress_order[session_id].get(key, 0) + new_food_dict.get(key, 0)
            inprogress_order[session_id] = result
        else:
            inprogress_order[session_id] = new_food_dict

        order_str = get_str_from_food_dict(inprogress_order[session_id])
        return jsonify({"fulfillmentText": f"So far you have {order_str}. Do you want anything else?"})

def remove_order(parameters: dict, session_id):
    if session_id not in inprogress_order:
        return jsonify({"fulfillmentText": "I am having trouble finding your order. Please place a new order."})

    current_food_dict = inprogress_order[session_id]
    food_item = parameters['food-item']

    removed = []
    no_item = []

    for item in food_item:
        if item not in current_food_dict:
            no_item.append(item)
        else:
            removed.append(item)
            del current_food_dict[item]

    fulfillment_text = ""
    if len(removed) > 0:
        fulfillment_text += f"We have removed {', '.join(removed)} from your order list.\n"
    if len(no_item) > 0:
        fulfillment_text += f"Your current order does not have {', '.join(no_item)}.\n"
    if len(current_food_dict.keys()) == 0:
        fulfillment_text += "Your order is empty."
    else:
        order_str = get_str_from_food_dict(current_food_dict)
        fulfillment_text += f"Here is what is left in your order: {order_str}. Anything else you want?"

    return jsonify({"fulfillmentText": fulfillment_text})

def complete_order(parameters: dict, session_id):
    if session_id not in inprogress_order:
        fulfillment_text = "I am having trouble finding your order. Sorry! Can you place a new order?"
    else:
        order = inprogress_order[session_id]
        order_id = save_to_db(order)
        if order_id == -1:
            fulfillment_text = "Sorry, I could not place your order due to a backend error. Please place a new order again."
        else:
            order_total = get_order_total(order_id)
            fulfillment_text = "Awesome! We have placed your order." \
                               f"Here is your order id: {order_id}. " \
                               f"Your order bill is {order_total}, which you can pay at the time of delivery."
        del inprogress_order[session_id]  # this will remove placed order from dict

    return jsonify({"fulfillmentText": fulfillment_text})

def save_to_db(order: dict):
    next_order_id = get_next_order_id()
    for food_items, quantity in order.items():
        rcode = insert_order_item(food_items, quantity, next_order_id)
        if rcode == -1:
            return -1
    insert_order_tracking(next_order_id, "in progress")
    return next_order_id

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.debug(f"Received data: {data}")

    intent = data["queryResult"]["intent"]["displayName"]
    logging.debug(f"Received intent: {intent}")

    parameters = data['queryResult']['parameters']
    logging.debug(f"Received parameters: {parameters}")

    query_result = data.get("queryResult", {})
    output_contexts = query_result.get("outputContexts", [])
    session_id = extract_session_id(output_contexts[0]["name"])
    logging.debug(f"Session ID: {session_id}")

    intent_handler_dict = {
        'track.order': track_order,
        'order.add': add_order,
        'order.complete': complete_order,
        'order.remove': remove_order,
        'new.order': new_order,
        'order-add-context:ongoing-order': add_order,
        'order-complete-context:ongoing-order': complete_order,
        'order-remove-context:ongoing-order': remove_order,
        'track-order-context:ongoing-tracking': track_order
    }

    if intent in intent_handler_dict:
        function = intent_handler_dict[intent]
        return function(parameters, session_id)
    else:
        logging.error(f"Unhandled intent: {intent}")
        return jsonify({"fulfillmentText": "Sorry, I don't understand this request."})

def new_order(parameters: dict, session_id):
    inprogress_order[session_id] = {}
    return jsonify({"fulfillmentText": "Starting new order. Specify food items and quantities. For example, you can say, I would like to order two pizzas and one mango lassi."})

if __name__ == "__main__":
    app.run(debug=True)