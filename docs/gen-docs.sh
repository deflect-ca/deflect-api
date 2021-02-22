python manage.py generateschema --title 'Deflect Core API Documentation' --format openapi-json > docs/schema.json
python manage.py docs_proc -i docs/schema.json -o docs/schema-altered.json
apistar docs --path docs/schema-altered.json --format openapi --theme swaggerui --serve
