import openai
from openai import OpenAIError

def explain_prediction(input_features, predicted_price):
    prompt = f"""
You are an automotive pricing analyst.

A vehicle has the following features:
{input_features}

The predicted market price is ${predicted_price:,.2f}.

Explain in 2-3 sentences why this price is reasonable, considering the features and market trends.
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    
        # response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",  # or "gpt-3.5-turbo"
        # messages=[{"role": "user", "content": prompt}],
        # temperature=0.7
        # )

        # return response['choices'][0]['message']['content']
    except OpenAIError as e:
        # Fallback explanation if API call fails
        print(f"OpenAI API error: {e}. Returning fallback explanation.")
        return (
            f"Based on the vehicle features {input_features} and market conditions, "
            f"a predicted price of ${predicted_price:,.2f} is reasonable."
        )
