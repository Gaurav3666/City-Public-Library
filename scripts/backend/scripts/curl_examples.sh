```bash
#!/usr/bin/env bash

# City Public Library API examples
# Start the FastAPI server before running these commands.
# Update IDs and credentials to match your database.

BASE_URL="http://127.0.0.1:8000"

echo "1. Check API health"
curl -i "$BASE_URL/"

echo ""
echo "2. List books"
curl -i "$BASE_URL/books/"

echo ""
echo "3. Register a member"
curl -i -X POST "$BASE_URL/members/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Member",
    "email": "demo.member@example.com",
    "password": "DemoMember@123"
  }'

echo ""
echo "4. Member login"
curl -i -X POST "$BASE_URL/members/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "aarav@example.com",
    "password": "LibraryDemo@123"
  }'

echo ""
echo "5. Partner catalogue without credentials (expected: 401)"
curl -i "$BASE_URL/partner/books"

echo ""
echo "6. Partner catalogue with credentials"
read -r -p "Enter partner API key: " PARTNER_API_KEY
read -r -s -p "Enter partner API secret: " PARTNER_API_SECRET
echo ""

curl -i "$BASE_URL/partner/books" \
  -H "X-API-Key: $PARTNER_API_KEY" \
  -H "X-API-Secret: $PARTNER_API_SECRET"

echo ""
echo "7. Request a protected member endpoint without a token (expected: 401)"
curl -i "$BASE_URL/members/me"

echo ""
echo "Examples completed."
```