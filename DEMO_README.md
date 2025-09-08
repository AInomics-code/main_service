# AI Service Demo Setup

## Quick Setup

### 1. Activate environment
```bash
conda activate ainomics
```

### 2. Create demo database
```bash
python create_demo_db.py
```

### 3. Configure environment variables
Create a `.env` file with:
```
OPENAI_KEY=your-openai-key-here
SQLSERVER_URL=sqlite:///demo_database.db
AWS_ACCESS_KEY_ID=demo-key
AWS_SECRET_ACCESS_KEY=demo-secret  
OPENSEARCH_ENDPOINT=demo-endpoint
```

### 4. Run the service

**Option A: Direct Python**
```bash
python -m uvicorn main:app --reload
```

**Option B: Docker (recommended for production-like demo)**
```bash
# Build the image
docker build -t ai-service-demo .

# Run with your OpenAI key
docker run -p 8000:8000 -e OPENAI_KEY=your-key-here ai-service-demo
```

## Sample Data Created

- **30 products** (including Hellmanns Mayonnaise, Organic Valley Milk, etc.)
- **50 customers** distributed across US cities
- **200 orders** with dates from the last year

## Testing

```bash
# Test SQLite connection and basic queries
python test_quick_query.py

# Test product search (requires OpenSearch setup)
python test_product_search.py

# Test complete flow
python test_full_flow.py
```

## API Endpoint

```
POST http://localhost:8000/api/v1/invoke
{
  "message": "How many products do we have in total?"
}
```

## Sample Queries

- "What products do we have from Hellmanns?"
- "How many customers are in New York?"
- "What are our best selling products?"
- "Show me all pending orders"
