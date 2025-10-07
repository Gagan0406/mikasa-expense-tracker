from langchain.prompts import PromptTemplate
prompt = PromptTemplate(template="""you will be given a message of user,you have to classify wether the user wants advice related to money , took some action with money like gained or loss , sent or recived or not talking about money as "action taken" , "needs advice" ,"other topic".
rules for "action taken"(sent or recived money,gained or lossed money) are:
- if user recieved money
- if user sent money
- if user gave loan
- if user took loan
- if user purchased something
- if user sold something and recived money for that
- if user recieved salary
- if user recieved bonuses
- if user made some income
- if user paid for expenses
- if user paid for bills and rent
- if user paid for the fees
- if user got some refund or lottery
- if user lost money in some investment or gambling
(you have to be wise enough to categorise tbis category mind it you have to make sure that first the action is taken with money and then only you have to classify it in this category not else , in this case we will be upadting the database related to user as action is being taken with money)

rules for "needs advice" (advice related to investment or market or expenditure or savings or any financial advice) are:
- if user is asking for investment advice
- if user is asking for market trends
- if user is asking for savings advice
- if user is asking for expenditure advice
- if user is asking for financial advice
- if user is asking for tax advice
- if user is asking for budget advice
- if user is asking for retirement advice
- if user is asking for insurance advice
- if user is asking for debt advice
- if user is asking for credit advice
- if user is asking for loan advice
- at what percent should we give or take the loan 
- is loan beneficial or not
- if user is asking for tips to manage money
(in this no action has been taken user is just asking for advice related to money in this case we will not be updating any database related to user,
 in this case we will be providing advice to user related to money,and only in this case you will classify to this category only not in any other case)
 
rules for "other topic" (not related to money or finance):
(anything which is not related to money or finance but if user is asking about currency convert or general questions like stock price of a company, then only classify to this category)

**(differentiate between "needs advice" and "other topic" carefully if user is asking for advice related to money then classify to "needs advice" category only not to this category,if user is asking for a fact check for the price of a stock and things like that then only classify to this category not to "needs advice" category)**

\nuser message:{input}:""",
input_variables=["input"])

prompt.save("category_of_message_prompt.json")



operation_prompt = PromptTemplate(
    input_variables=["user_msg"],
    template="""
You are an intelligent text classifier. 
Your task is to analyze the given user message and decide what type of database operation it represents.  
The database stores financial transactions (money received, money sent, salary, bonus, loans, corrections, etc.).

The possible operations are:
1. Insert  → Adding new transaction data
2. Update  → Correcting or modifying an existing transaction
3. Retrieve → Asking to view or check past transactions
4. Delete  → Removing an already inserted transaction

Guidelines:
- If the user is telling about **a new transaction**, it is an Insert.
- If the user is **correcting or changing** a previous transaction (like wrong amount, wrong category), it is an Update.
- If the user is **asking to see, check, or fetch** some record, it is a Retrieve.
- If the user wants to **remove or cancel** a transaction, it is a Delete.

Examples:

Insert:
- "I got 2000 rupees as pocket money."
- "I spent 500 on food yesterday."
- "Salary credited of 50,000 this month."
- "Paid 1200 rent to landlord."

Update:
- "Sorry, not 2000, it was 1800."
- "Change the amount of the food expense to 450."
- "Update my last transaction, it was shopping not groceries."

Retrieve:
- "Show me my last 5 transactions."
- "How much money did I spend on food this month?"
- "What is my total salary credited till now?"
- "List all expenses for August."

Delete:
- "Delete the last transaction."
- "Remove the pocket money entry."
- "Cancel the record of 1200 rent."
- "Forget what I said about getting 500."

Now, classify the following user message into one of the four categories:
User message: "{user_msg}"

Answer with only ONE word: Insert, Update, Retrieve, or Delete.
"""
)

operation_prompt.save('crud_operation_prompt.json')


transaction_info_extraction_prompt = PromptTemplate(
    input_variables=["user_message"],
    template="""
You are an information extractor.  
Your task is to read the user's message and extract the following fields for a financial transaction:

1. transaction_type: "credit" if the user received money, "debit" if the user spent money  
2. amount: numeric value of money involved  
3. description: short description (spent on what / received from whom)

User message: "{user_message}"

Extract the data carefully. If the information is missing, infer from the context.
Return only valid values that match the schema.
"""
)
transaction_info_extraction_prompt.save('transaction_info_extraction_prompt.json')



insert_query_prompt = PromptTemplate(
    input_variables=["transaction_type", "amount", "description"],
    template="""
You are an expert SQL query generator. 
Your task is to create a **PostgreSQL INSERT query** for storing financial transactions in the following schema:

Schema:
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(10) CHECK (transaction_type IN ('credit','debit')),
    amount NUMERIC NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Rules:
1. Always insert into `transaction_type`, `amount`, and `description` columns. 
2. Do NOT include `id` or `created_at` in the query (Postgres will auto-generate them).
3. Use correct SQL syntax with single quotes for text values.
4. The transaction_type must always be either 'credit' or 'debit'.
5. Output only the SQL query string.

Examples of correct queries:
INSERT INTO transactions (transaction_type, amount, description)
VALUES ('credit', 2000, 'pocket money');

INSERT INTO transactions (transaction_type, amount, description)
VALUES ('debit', 500, 'grocery shopping');

INSERT INTO transactions (transaction_type, amount, description)
VALUES ('credit', 10000, 'salary for September');

Now generate a valid PostgreSQL INSERT statement for these values:

- transaction_type: {transaction_type}
- amount: {amount}
- description: {description}
"""
)

insert_query_prompt.save('insert_query_prompt.json')



update_prompt = PromptTemplate(
    input_variables=["user_message"],
    template="""
You are an expert PostgreSQL query generator. Your sole task is to generate a single, valid PostgreSQL UPDATE query based on a user's natural language request.

The table schema you must use is:

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(10) CHECK (transaction_type IN ('credit','debit')),
    amount NUMERIC NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Goal:
- Generate a single valid PostgreSQL UPDATE query based on the user_message.
- Output ONLY the SQL query string.
- If the user's message is ambiguous or does not specify what to update or which record to update, respond with the exact phrase: "I need more information to safely update data. Please provide specific criteria for the changes and the record(s) to be updated."

General Rules:
1.  **ALWAYS** use a `WHERE` clause. Never generate an `UPDATE` query without one.
2.  Infer what fields to SET and what values to use from the user_message.
3.  Infer the criteria for the `WHERE` clause from the user_message.
4.  For description matching, use `description ILIKE '%<keyword>%'` for case-insensitive, partial matches.
5.  Always apply the update to the most recent matching record using `ORDER BY created_at DESC LIMIT 1` unless the user explicitly specifies an ID or multiple records.
6.  The output must be a valid SQL UPDATE statement for PostgreSQL.

Examples:

A) Update a description and amount for a specific ID
Input: user_message = "change the amount of transaction 123 to 200 and description to 'new description'"
SQL:
UPDATE transactions SET amount = 200, description = 'new description' WHERE id = 123;

B) Update amount for the latest transaction matching a description
Input: user_message = "I want to change the amount for my last 'food' transaction to 45.50"
SQL:
UPDATE transactions SET amount = 45.50 WHERE description ILIKE '%food%' ORDER BY created_at DESC LIMIT 1;

C) Update transaction type for the latest record
Input: user_message = "change my last credit transaction to a debit"
SQL:
UPDATE transactions SET transaction_type = 'debit' WHERE transaction_type = 'credit' ORDER BY created_at DESC LIMIT 1;

D) Update amount for a specific description
Input: user_message = "update the amount for the 'gas' transaction to 80"
SQL:
UPDATE transactions SET amount = 80 WHERE description ILIKE '%gas%' ORDER BY created_at DESC LIMIT 1;

E) Update multiple fields for the latest matching record
Input: user_message = "set the amount to 1000 and description to 'rent' for the most recent debit"
SQL:
UPDATE transactions SET amount = 1000, description = 'rent' WHERE transaction_type = 'debit' ORDER BY created_at DESC LIMIT 1;

F) Update based on a time constraint
Input: user_message = "change the amount for all transactions from last month to 0"
SQL:
UPDATE transactions SET amount = 0 WHERE created_at >= date_trunc('month', now()) - INTERVAL '1 month' AND created_at < date_trunc('month', now());

G) Update based on a numeric condition
Input: user_message = "increase the amount of all transactions with amount less than 50 by 10"
SQL:
UPDATE transactions SET amount = amount + 10 WHERE amount < 50;

H) Vague update request (model should refuse)
Input: user_message = "update something"
SQL:
I need more information to safely update data. Please provide specific criteria for the changes and the record(s) to be updated.

Now generate the PostgreSQL UPDATE query for this input:
User message: {user_message}

Output only the SQL query string.
"""
)

update_prompt.save('update_query_prompt.json')





retrieve_prompt = PromptTemplate(
    input_variables=["user_message"],
    template="""
You are an expert PostgreSQL query generator for the following table:

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(10) CHECK (transaction_type IN ('credit','debit')),
    amount NUMERIC NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Goal:
- Generate a single valid PostgreSQL SELECT query based on the natural-language user_message.
- Output ONLY the SQL query string (no explanations, no backticks).

General rules:
1. If the user asks for totals/amounts (keywords: "total", "sum", "how much", "what is the total", "total spent", "total received"), use SUM(amount) and name it (e.g. SUM(amount) AS total_spent).
2. For averages use AVG(amount); for counts use COUNT(*) or COUNT(id); for max/min use MAX(amount)/MIN(amount).
3. Time phrases:
    - "this month" -> created_at >= date_trunc('month', now())
    - "last month" -> created_at >= date_trunc('month', now()) - INTERVAL '1 month' AND created_at < date_trunc('month', now())
    - "today" -> created_at >= date_trunc('day', now())
    - "last 7 days" -> created_at >= now() - INTERVAL '7 days'
    - "between YYYY-MM-DD and YYYY-MM-DD" -> created_at BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'
    - If a precise time window is mentioned use it (convert to created_at filters).
4. Description matching: prefer flexible match: `description ILIKE '%<description>%'` (case-insensitive substring).
5. Infer transaction_type from context (e.g., "money spent" implies 'debit', "money received" implies 'credit').
6. amount handling:
    - Infer numerical values and comparative words from the user_message.
    - If user_message contains comparative words like "above", "over", "greater than", use `amount > x`.
    - If it contains "less than", "below", "under", use `amount < x`.
    - Otherwise (explicit equality expressed like "exactly 200"), use `amount =x`.
7. If the user asks for "per category", "by description", "group by", produce GROUP BY with aggregates and optional HAVING.
8. If no filters provided, generate a safe default (e.g. `SELECT * FROM transactions;`) or an aggregate default if user asks for total.
9. Use ORDER BY and LIMIT only when user asks (e.g., "latest 5", "top 3 categories").
10. Always ensure proper SQL syntax and single quotes around text.

Examples (these are examples the model should pattern-match):

A) Simple retrieve all
Input: user_message = "show all transactions"
SQL:
SELECT * FROM transactions;

B) Retrieve only credits
Input: user_message = "show credits"
SQL:
SELECT * FROM transactions WHERE transaction_type = 'credit';

C) Total spent on food this month
Input: user_message = "total spent on food this month?"
SQL:
SELECT SUM(amount) AS total_spent
FROM transactions
WHERE transaction_type = 'debit'
  AND description ILIKE '%food%'
  AND created_at >= date_trunc('month', now());

D) Total credited between two dates
Input: user_message = "total credits between 2025-08-01 and 2025-08-31"
SQL:
SELECT SUM(amount) AS total_received
FROM transactions
WHERE transaction_type = 'credit'
  AND created_at BETWEEN '2025-08-01' AND '2025-08-31';

E) Average debit per category for the year
Input: user_message = "average monthly spending by category this year"
SQL:
SELECT description, AVG(amount) AS avg_spent
FROM transactions
WHERE transaction_type = 'debit'
  AND created_at >= date_trunc('year', now())
GROUP BY description
ORDER BY avg_spent DESC;

F) Categories where total spending > 5000
Input: user_message = "categories where total spending greater than 5000"
SQL:
SELECT description, SUM(amount) AS total_spent
FROM transactions
WHERE transaction_type = 'debit'
GROUP BY description
HAVING SUM(amount) > 5000
ORDER BY total_spent DESC;

G) Latest 5 transactions
Input: user_message = "show my last 5 transactions"
SQL:
SELECT * FROM transactions ORDER BY created_at DESC LIMIT 5;

H) Debits above a threshold (comparison)
Input: user_message = "show debits above 1000"
SQL:
SELECT * FROM transactions WHERE transaction_type = 'debit' AND amount > 1000 ORDER BY created_at DESC;

I) Retrieve using substring match
Input: user_message = "show rides"
SQL:
SELECT * FROM transactions WHERE description ILIKE '%uber%' ORDER BY created_at DESC;

J) Monthly spending trend (grouped by month)
Input: user_message = "monthly spending trend"
SQL:
SELECT DATE_TRUNC('month', created_at) AS month, SUM(amount) AS total_spent
FROM transactions
WHERE transaction_type = 'debit'
GROUP BY month
ORDER BY month;

Now generate the best PostgreSQL SELECT query for this input:
User message: {user_message}

Output only the SQL query string.
"""
)

retrieve_prompt.save('retrieve_query_prompt.json')


delete_prompt = PromptTemplate(
    input_variables=["user_message"],
    template="""
You are an expert PostgreSQL query generator. Your sole task is to generate a single, valid PostgreSQL DELETE query based on a user's natural language request.

The table schema you must use is:

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(10) CHECK (transaction_type IN ('credit','debit')),
    amount NUMERIC NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Goal:
- Generate a single valid PostgreSQL DELETE query based on the user_message.
- Output ONLY the SQL query string.
- If the user's message is ambiguous or does not specify clear criteria for deletion (e.g., "delete something"), respond with the exact phrase: "I need more information to safely delete data. Please provide specific criteria."

General Rules:
1.  **ALWAYS** use a `WHERE` clause. Never generate a `DELETE` query without one.
2.  Infer criteria from the user_message. This includes matching conditions for `id`, `transaction_type`, `amount`, `description`, and `created_at`.
3.  For description matching, use `description ILIKE '%<keyword>%'` for case-insensitive, partial matches.
4.  For numeric comparisons on `amount`, use `=`, `>`, `<`, `>=`, or `<=` as inferred from the user's message.
5.  For date and time filters on `created_at`, interpret phrases like "last month", "yesterday", or specific dates to create appropriate `WHERE` clauses (e.g., `created_at >= 'YYYY-MM-DD'`).

Examples:

A) Delete by ID
Input: user_message = "delete the transaction with id 123"
SQL:
DELETE FROM transactions WHERE id = 123;

B) Delete by transaction type
Input: user_message = "remove all debit transactions"
SQL:
DELETE FROM transactions WHERE transaction_type = 'debit';

C) Delete based on amount
Input: user_message = "delete any transactions with an amount of 500"
SQL:
DELETE FROM transactions WHERE amount = 500;

D) Delete by partial description match
Input: user_message = "remove all transactions related to 'uber' rides"
SQL:
DELETE FROM transactions WHERE description ILIKE '%uber%';

E) Delete transactions older than a specific date
Input: user_message = "delete all transactions before 2024-01-01"
SQL:
DELETE FROM transactions WHERE created_at < '2024-01-01';

F) Delete with multiple conditions (AND)
Input: user_message = "remove any debit transactions for 'food' from last month"
SQL:
DELETE FROM transactions WHERE transaction_type = 'debit' AND description ILIKE '%food%' AND created_at >= date_trunc('month', now()) - INTERVAL '1 month' AND created_at < date_trunc('month', now());

G) Delete with multiple conditions (OR)
Input: user_message = "delete any transactions with a description of 'rent' or 'mortgage'"
SQL:
DELETE FROM transactions WHERE description ILIKE '%rent%' OR description ILIKE '%mortgage%';

H) Delete based on a numeric comparison
Input: user_message = "remove all credits with an amount less than 100"
SQL:
DELETE FROM transactions WHERE transaction_type = 'credit' AND amount < 100;

I) Delete oldest transactions
Input: user_message = "delete the oldest 5 transactions"
SQL:
DELETE FROM transactions WHERE id IN (SELECT id FROM transactions ORDER BY created_at ASC LIMIT 5);

J) Ambiguous deletion request (model should refuse)
Input: user_message = "delete something from my account"
SQL:
I need more information to safely delete data. Please provide specific criteria.

Now generate the PostgreSQL DELETE query for this input:
User message: {user_message}

Output only the SQL query string.
"""
)

delete_prompt.save('delete_query_prompt.json')



query_evaluator_prompt = PromptTemplate(
    input_variables=["user_message", "query"],
    template="""
You are an expert PostgreSQL query evaluator. Your task is to meticulously evaluate a given SQL query based on a user's original request, ensuring it is correct and safe.

You will be provided with two key inputs:

1. `user_message`: The user's original natural language request.
2. `query`: The PostgreSQL query to be evaluated.

The database schema is as follows:

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(10) CHECK (transaction_type IN ('credit','debit')),
    amount NUMERIC NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Your evaluation must follow these rules:

**Evaluation Rules:**

1. **Intent Match:** Does the `query` accurately reflect the meaning and intent of the `user_message`?

2. **Safety:**
   * For `DELETE` and `UPDATE` queries, is a `WHERE` clause present? A query without a `WHERE` clause is a critical safety failure and must be rejected.
   * Does the `WHERE` clause correctly and safely narrow down the affected records?

3. **Correctness:**
   * Is the SQL syntax valid for PostgreSQL?
   * Does the query use the correct table and column names from the provided schema?
   * Are string literals enclosed in single quotes?

4. **Output Format:** Your final response must be a JSON object with the following structure:
   * `feedback` (string): A detailed, natural language explanation of your evaluation. It should describe what the query does, if it's correct, any issues found, and the reason for the approval status.
   * `query_approved` (string, either "yes" or "no"): Your final judgment on the query. It should be "yes" only if the query is safe and correctly matches the intent.

**Examples for Guidance:**

**A) Correct and Optimal Query**
* `user_message`: "total credits between 2024-01-01 and 2024-01-31"
* `query`: `SELECT SUM(amount) AS total_received FROM transactions WHERE transaction_type = 'credit' AND created_at BETWEEN '2024-01-01' AND '2024-01-31';`
* **Evaluation:**
  * `feedback`: "The query correctly calculates the total amount for 'credit' transactions within the specified date range. The `WHERE` clause is accurate and the aggregation function is correct."
  * `query_approved`: "yes"

**B) Correct but Needs Optimization**
* `user_message`: "show all credit transactions that are exactly 500"
* `query`: `SELECT * FROM transactions WHERE transaction_type = 'credit' AND amount LIKE '500';`
* **Evaluation:**
  * `feedback`: "The query correctly identifies transactions with a transaction type of 'credit' and an amount of 500. However, using `LIKE` on a numeric column is incorrect. Using `=` is the proper way to check for equality with a numeric value."
  * `query_approved`: "yes"

**C) Dangerous and Incorrect Query**
* `user_message`: "delete all debit transactions with id 100"
* `query`: `DELETE FROM transactions;`
* **Evaluation:**
  * `feedback`: "The query is extremely dangerous. It attempts to delete ALL records from the `transactions` table without a `WHERE` clause. This violates a critical safety rule and does not match the user's intent to delete a specific transaction. The query is rejected."
  * `query_approved`: "no"

**D) Logical Mismatch**
* `user_message`: "What is the average amount for debit transactions?"
* `query`: `SELECT COUNT(*) FROM transactions WHERE transaction_type = 'debit';`
* **Evaluation:**
  * `feedback`: "The query is syntactically correct and safely filters by transaction type. However, it counts the transactions instead of calculating the average amount as requested by the user. The logical intent is incorrect, so the query is rejected."
  * `query_approved`: "no"

**Perform the evaluation for the following inputs:**
User Message: {user_message}
Query: {query}
"""
)
query_evaluator_prompt.save('query_evaluator_prompt.json')



query_optimizer_prompt = PromptTemplate(
    input_variables=["user_message", "query", "query_feedback"],
    template="""
You are an expert PostgreSQL query optimizer. Your task is to take an initial SQL query and improve it based on provided feedback, ensuring the final query is correct, safe, and efficient. You must also consider the original user's intent.

The database schema is as follows:

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(10) CHECK (transaction_type IN ('credit','debit')),
    amount NUMERIC NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Your evaluation and optimization must follow these rules:

**Optimization Rules:**
1.  **Read and Understand:** Carefully read the `user_message`, `query`, and `query_feedback` to understand the problem with the original query.
2.  **Correctness:** Fix any syntax errors, logical errors, or data type mismatches mentioned in the feedback.
3.  **Safety:** For `DELETE` and `UPDATE` queries, ensure a safe `WHERE` clause exists to prevent unintended data loss. If the feedback indicates a missing `WHERE` clause, add one based on the `user_message`.
4.  **Efficiency:** Replace inefficient patterns with more optimal ones. For example, use `=` instead of `LIKE` when comparing numeric values.
5.  **Maintain Intent:** The final improved query must accurately fulfill the user's original request from the `user_message`.

**Examples for Guidance:**

**A) Fixing a Data Type Mismatch**
* `user_message`: "show all credit transactions that are exactly 500"
* `query`: `SELECT * FROM transactions WHERE transaction_type = 'credit' AND amount LIKE '500';`
* `query_feedback`: "The query correctly identifies transactions with a transaction type of 'credit' and an amount of 500. However, using `LIKE` on a numeric column is incorrect. Using `=` is the proper way to check for equality with a numeric value."
* `improved_query`: `SELECT * FROM transactions WHERE transaction_type = 'credit' AND amount = 500;`

**B) Fixing a Logical Mismatch**
* `user_message`: "What is the average amount for debit transactions?"
* `query`: `SELECT COUNT(*) FROM transactions WHERE transaction_type = 'debit';`
* `query_feedback`: "The query is syntactically correct and safely filters by transaction type. However, it counts the transactions instead of calculating the average amount as requested by the user. The logical intent is incorrect, so the query is rejected."
* `improved_query`: `SELECT AVG(amount) FROM transactions WHERE transaction_type = 'debit';`

**C) Fixing a Dangerous Query**
* `user_message`: "delete all debit transactions with id 100"
* `query`: `DELETE FROM transactions;`
* `query_feedback`: "The query is extremely dangerous. It attempts to delete ALL records from the `transactions` table without a `WHERE` clause. This violates a critical safety rule and does not match the user's intent to delete a specific transaction. The query is rejected."
* `improved_query`: `DELETE FROM transactions WHERE transaction_type = 'debit' AND id = 100;`

Now, provide the single, improved query string for these inputs:
User Message: {user_message}
Query: {query}
Query Feedback: {query_feedback}
"""
)
query_optimizer_prompt.save('query_optimizer_prompt.json')