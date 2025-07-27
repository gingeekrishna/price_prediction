# import openai
# from openai import OpenAIError

# class ExplainerAgent:
#     def __init__(self, model="gpt-3.5-turbo"):
#         self.model = model

#     def explain(self, input_data: dict, price: float):
#         prompt = f"Explain why a vehicle with the following data:\n{input_data}\nwas priced at ${price:.2f}."
#         try:
#             response = openai.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.7
#         )
#             return response.choices[0].message.content.strip()
#         except OpenAIError as e:
#             # Fallback explanation if API call fails
#             print(f"OpenAI API error: {e}. Returning fallback explanation.")
#             return (
#                 f"Based on the vehicle features {input_data} and market conditions, "
#                 f"a predicted price of ${price:.2f} is reasonable."
#             )
    
from src.mock import DummyEmbeddings, DummyChatCompletion
from langchain.vectorstores import FAISS

class ExplainerAgentRAG:
    def __init__(self, use_mock=True):
        if use_mock:
            self.embeddings = DummyEmbeddings()
            self.chat_completion = DummyChatCompletion()
            self.vectorstore = None
        else:
            from langchain.embeddings import OpenAIEmbeddings
            import openai
            self.embeddings = OpenAIEmbeddings()
            self.chat_completion = openai.chat.completions
            self.vectorstore = FAISS.load_local("faiss_index", self.embeddings)
            print(f"Loaded FAISS index with {self.vectorstore.index.ntotal} vectors.")

    def explain(self, input_data, predicted_price):
        # Convert input_data to a query string or text for retrieval
        query_text = str(input_data)

        # Use vectorstore to retrieve relevant docs if available
        relevant_docs = []
        if self.vectorstore:
            relevant_docs = self.vectorstore.similarity_search(query_text, k=3)
            # You can log what docs you got
            print("Retrieved documents for explanation:", relevant_docs)

        # Build prompt including relevant docs context
        context_text = "\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else ""
        prompt = (
            f"Context: {context_text}\n\n"
            f"Explain why a vehicle with features {input_data} is priced at ${predicted_price:.2f}."
        )
        if hasattr(self, 'chat_completion') and isinstance(self.chat_completion, DummyChatCompletion):
            response = self.chat_completion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        else:
            response = self.chat_completion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
        return response["choices"][0]["message"]["content"]
