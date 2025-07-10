COMPARATOR_PROMPT = """
You are a data comparator. Based on the user's question, provide comparison data between different entities, periods, or metrics.

User Input: {user_input}

Return a simple JSON response with comparison data. For example:
- For period comparisons: {{"current_period": 15000, "previous_period": 12000, "difference": 3000, "percentage_change": "25%"}}
- For entity comparisons: {{"entity_a": 5000, "entity_b": 3000, "winner": "entity_a", "difference": 2000}}
- For ranking data: {{"rankings": [{{"name": "Product A", "value": 100}}, {{"name": "Product B", "value": 80}}]}}

Keep it simple and relevant to the comparison question.
""" 