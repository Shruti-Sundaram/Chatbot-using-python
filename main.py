import re
from nltk import pos_tag
from nltk.tokenize import word_tokenize
import pandas as pd
import nltk
nltk.download('averaged_perceptron_tagger')

#for qa dataset
data=pd.read_csv("chatbot_dataset.csv")
df_raw=pd.DataFrame(data)

inp_out={}
success_count=0
error_count=0

for i in range(0,df_raw['Input'].count()):
    inp_out[df_raw['Input'][i]]=df_raw['Output'][i]


# Download nltk resources
import nltk
nltk.download('punkt')

# List of predefined intents and responses
intents_data = {
    "greeting": ["hello", "hi", "hey", "greetings"],
    "farewell": ["bye", "goodbye", "see you later", "take care"],
    "identity": ["name", "am", "my name is", "I am", "what's", "your", "name"],
    "thanks": ["thank you", "thanks", "appreciate it", "appreciate", "thank"],
    "wcud" : [ "can", "do"],
    "default": ["default response"],
    "retrieval": ["what's", "my", "name", "say", "who", "am", "i"],
    "greeting reply": ["am", "good", "great"],
    "order": ["order", "menu"],
    "restaurant": ["bella", "italia", "chopstix", "ginza", "bistro", "live"],
    "description1": ["11","12","13"],
    "description2": ["21","22","23"],
    "description3": ["31","32","33"],
    "description4": ["41","42","43"],
    "add": ["add"],
    "continue": ["continue"],
    "back": ["back"],
    "confirm": ["confirm"],
    "discard": ["discard"]

}

# Identity management dictionary
user_identities = {}

# Function for data cleaning using regular expressions
def clean_text(text):
    # Convert to lowercase and remove non-alphanumeric characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
    return text

# Function to calculate Jaccard similarity
def calculate_jaccard_similarity(user_input, intent_phrases):
    user_tokens = set(user_input.split())
    intent_tokens = set(intent_phrases)

    intersection = len(user_tokens.intersection(intent_tokens))
    union = len(user_tokens.union(intent_tokens))

    similarity = intersection / union if union != 0 else 0
    return similarity

# Function to identify user intent
def identify_intent(user_input, intents_data):
    max_similarity = 0
    identified_intent = "default"

    for intent, phrases in intents_data.items():
        similarity = calculate_jaccard_similarity(user_input, phrases)
        #print(user_input,":",phrases,":",similarity)
        if similarity > max_similarity:
            max_similarity = similarity
            identified_intent = intent
    #print(max_similarity)
    if max_similarity<0.125:
       identified_intent = "qa"

    return identified_intent

# Function to handle user identity using POS tagging
def handle_identity(user_input):
    tokens = word_tokenize(user_input)
    pos_tags = pos_tag(tokens)
    user_name = None
    for token, tag in pos_tags:
        #Check for proper and common nouns
        if tag in ['NNP', 'NN','JJ'] and token not in ['name','Name', 'I', 'i']:
            user_name = token
            break
    return user_name

# menu dataset
data = pd.read_csv("menu.csv")
df = pd.DataFrame(data)

# Function to display restaurants
def res():
    print("\tBella Italia")
    print("\tChopstix")
    print("\tGinza")
    print("\tBistro Live\n")


# Function to display menu items
def menu(x):
    filtered_df = df[df['restaurant'] == x.lower()]
    id = filtered_df['id']
    dish = filtered_df['dish']
    price = filtered_df['price']
    combined_values = pd.concat([id, dish, price], axis=1)
    print("")
    print(combined_values.to_string(index=False))
    print("")
    print("Type in the id number of a dish to get more info about it.")
    print("OR Type 'add' to place an order.")
    print("")

# Function to describe dishes
def describe(x):
    global success_count
    fil_df = df[df['id'] == float(x)]
    info = fil_df[['description']]
    print(info.to_string(index=False))
    print("")
    print("   Type 'back' to view other restaurants")
    print("   OR")
    print("   Type 'add' to place an order.")
    success_count+=1
    print("")

dish=[]
quantity=[]
#Function to place order
def add(x):
    print("Chatbot: Please specify your selected dish and quantity-")
    print("")
    dish_input = input("\tEnter Dish: ")
    dish.append(dish_input)
    quantity_input = int(input("\tEnter Quantity: "))
    quantity.append(quantity_input)

# Function to continue and calculate price
cost=0
price_lst=[]
def cont():
    global success_count
    for i in dish:
        filtered_df = df[df['dish'] == i.lower()]
        price = list(filtered_df['price'])
        #print(price)
        currency_str= str(price[0])
        currency=int(currency_str[1:])
        price_lst.append(int(currency))
    print("Chatbot: Here is your Order Summary ~\n")
    for element1, element2, element3 in zip(dish, price_lst, quantity):
        print("\t"f"{element1} (${element2}) : {element3}")
    result1 = [a * b for a, b in zip(price_lst, quantity)]
    result2 = sum(result1)
    print("\n\tTotal Bill is $"+str(result2))
    print("\nPlease type 'confirm' to proceed to payment OR type 'discard' to discard this order.")
    success_count+=1

# Confirm payment
card=[]
address=[]
def confirm():
    global error_count
    card_input= input("Chatbot: Please enter your card details[enter 16 digit code]: ")
    address_input=input("Chatbot: Please enter address for delivery[block,street,area]: ")
    
    if len(str(card_input).replace(" ", "").strip()) <16 and len(list(address_input.strip().split(' '))) <=3:
        print("The entries are not valid.\n")
        error_count+=1
        print("Please type 'confirm' to try again.")
        print("OR type 'back' to discard the order.")
    else:
        print("\n\tYour order has been successfully placed. Thank You!")




# Main function to run the chatbot
def chatbot():
    global success_count
    global error_count
    print("Chatbot: Hey there! (Type 'exit' to end the conversation)")

    is_greet = False
    while True:
        user_input = input("User: ")

        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break

        # Clean user input
        cleaned_input = clean_text(user_input)

        # Identify user intent
        intent = identify_intent(cleaned_input, intents_data)

        # Process user input based on identified intent
        if intent == "greeting":
            print("Chatbot: Hello! What is your name?")
            is_greet = True

        elif intent == "farewell":
            print("Chatbot: Goodbye! Have a great day.")

        elif intent == "thanks":
            print("Chatbot: You're welcome! If you have more questions, feel free to ask.")

        elif intent == "identity" or is_greet == True:
            user_name = handle_identity(user_input)
            if user_name:
                user_identities["user"] = user_name
                print(f"Chatbot: Nice to meet you, {user_name}! I'm FoodieFriend - your food order and delivery assistant. How can I assist you?")
            else:
                print("Chatbot: I didn't catch your name. Can you please provide it?")
            is_greet = False

        elif intent == "retrieval":
            print("Chatbot: " + user_name)

        elif intent == "wcud":
            print("Chatbot: I can answer your questions and assist you with placing your food orders.")

        elif intent == "greeting reply":
            print("Chatbot: That's great :)")

        elif intent == "order":
            print("Chatbot: Which restaurant would you like to order from:-")
            res()

        elif intent == "restaurant":
            print("Chatbot: Please choose from the following dishes:-")
            menu(user_input)
            print("Chatbot: Type 'back' to view other restaurants.\n")
            #success_count+=1

        elif intent == "back":
            res()

        elif intent == "description1" or intent == "description2" or intent == "description3" or intent == "description4":
            describe(user_input)

        elif intent == "add":
            add(user_input)
            print("")
            print("Type 'add' to add more dishes, or type 'continue' to proceed to your payment\n")
            success_count+=1

        elif intent == "continue":
            cont()

        elif intent == "confirm":
            confirm()

        elif intent == "discard":
            res()

        #Question-answering
        elif intent == "qa":
            max_similarity=0
            answer=''
            for inp, output in inp_out.items():
                cleaned_user_input = clean_text(user_input)
                cleaned_input = clean_text(inp)
                similarity = calculate_jaccard_similarity(cleaned_user_input, cleaned_input.split())
                if similarity > max_similarity:
                    max_similarity = similarity
                    answer = "Chatbot: "+output
            if max_similarity == 0:
                print("Chatbot: Sorry I can't understand.")
                error_count+=1
            print(answer)
        else:
            print("Chatbot: I'm not sure how to respond to that. Can you please provide more information?")
            error_count+=1
   
    per_met_intial = pd.read_csv("performance_testing.csv")
    per_met=pd.DataFrame(per_met_intial)
    row_count = per_met.shape[0]
    index_update = row_count+1
    error_rate = 0
    if success_count!= 0:
        error_rate = (error_count/success_count)*100
    

    
    per_met.at[index_update, 'Error count'] = error_count
    per_met.at[index_update, 'Success count'] = success_count
    per_met.at[index_update, 'Error rate'] = error_rate

    per_met.to_csv('performance_testing.csv', index=False)

    #error_count+=1
    #success_count+=1


# Run the chatbot
if __name__ == "__main__":
    chatbot()

