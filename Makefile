generate:
	alembic revision --m="$(NAME)" --autogenerate

migrate:
	alembic upgrade head

.PHONY: i18n extract update compile

i18n:
	@echo "Available commands: extract, update, compile"

extract:
	pybabel extract -F babel.cfg -o locales/messages.pot .

update:
	pybabel update -i locales/messages.pot -d locales

compile:
	pybabel compile -d locales